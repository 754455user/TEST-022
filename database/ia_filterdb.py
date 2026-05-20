# Don't Remove Credit @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import re, base64, logging
from struct import pack
from pyrogram.file_id import FileId
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError
from info import FILE_DB_URI, SEC_FILE_DB_URI, DATABASE_NAME, COLLECTION_NAME, MULTIPLE_DATABASE, USE_CAPTION_FILTER, MAX_B_TN

logger = logging.getLogger(__name__)

# First Database For File Saving
client = AsyncIOMotorClient(FILE_DB_URI)
db = client[DATABASE_NAME]
col = db[COLLECTION_NAME]

# Second Database For File Saving
sec_client = AsyncIOMotorClient(SEC_FILE_DB_URI)
sec_db = sec_client[DATABASE_NAME]
sec_col = sec_db[COLLECTION_NAME]


async def save_file(media):
    """Save file in the database."""
    try:
        file_id = unpack_new_file_id(media.file_id)
    except Exception as e:
        logger.error(f"Error unpacking file_id: {e}")
        return False, 2

    file_name = clean_file_name(getattr(media, 'file_name', '') or '')
    new_file_name = f"@VJ_Bots {file_name}"

    file = {
        'file_id': file_id,
        'file_name': new_file_name,
        'file_size': getattr(media, 'file_size', 0),
        'caption': media.caption.html if getattr(media, 'caption', None) else None
    }

    # Check duplicate
    if await is_file_already_saved(file_id, new_file_name):
        return False, 0

    try:
        await col.insert_one(file)
        logger.info(f"{file_name} saved successfully.")
        return True, 1
    except DuplicateKeyError:
        logger.info(f"{file_name} already exists.")
        return False, 0
    except Exception as e:
        if MULTIPLE_DATABASE:
            try:
                await sec_col.insert_one(file)
                logger.info(f"{file_name} saved to second DB.")
                return True, 1
            except DuplicateKeyError:
                return False, 0
            except Exception as e2:
                logger.error(f"Second DB error: {e2}")
                return False, 2
        else:
            logger.error("Database full! Enable MULTIPLE_DATABASE.")
            return False, 2


def clean_file_name(file_name):
    """Clean and format the file name."""
    file_name = re.sub(r"(_|\-|\.|\+)", " ", str(file_name))
    unwanted_chars = ['[', ']', '(', ')', '{', '}']
    for char in unwanted_chars:
        file_name = file_name.replace(char, '')
    old_file_name = ' '.join(filter(
        lambda x: not x.startswith('@') and
                  not x.startswith('http') and
                  not x.startswith('www.') and
                  not x.startswith('t.me'),
        file_name.split()
    ))
    new_file_name = add_space_between_e_and_number(old_file_name)
    return new_file_name


def add_space_between_e_and_number(input_string):
    output_string = re.sub(r'(e|E)([0-9])', r'\1 \2', input_string)
    return output_string


async def is_file_already_saved(file_id, file_name):
    """Check if the file is already saved in either collection."""
    for collection in [col, sec_col]:
        if await collection.find_one({'file_id': file_id}) or await collection.find_one({'file_name': file_name}):
            return True
    return False


async def get_search_results(chat_id, query, file_type=None, max_results=10, offset=0, filter=False):
    """For given query return (results, next_offset)"""
    query = query.strip()
    if not query:
        raw_pattern = '.'
    elif ' ' not in query:
        raw_pattern = r'(\b|[\.+\-_])' + query + r'(\b|[\.+\-_])'
    else:
        raw_pattern = query.replace(' ', r'.*[\s\.+\-_]')
    try:
        regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    except:
        regex = query

    filter_query = {'file_name': regex}
    files = []

    if MULTIPLE_DATABASE:
        async for file in col.find(filter_query).sort('$natural', -1).skip(offset).limit(max_results):
            files.append(file)
        async for file in sec_col.find(filter_query).sort('$natural', -1).skip(offset).limit(max_results):
            files.append(file)
        total_results = await col.count_documents(filter_query) + await sec_col.count_documents(filter_query)
    else:
        async for file in col.find(filter_query).sort('$natural', -1).skip(offset).limit(max_results):
            files.append(file)
        total_results = await col.count_documents(filter_query)

    next_offset = "" if (offset + max_results) >= total_results else (offset + max_results)
    return files, next_offset, total_results


async def get_bad_files(query, file_type=None, use_filter=False):
    """For given query return (results, total)"""
    query = query.strip()
    if not query:
        raw_pattern = '.'
    elif ' ' not in query:
        raw_pattern = rf'(\b|[.+\-_]){query}(\b|[.+\-_])'
    else:
        raw_pattern = query.replace(' ', r'.*[\s.+\-_]')
    try:
        regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    except re.error:
        return [], 0

    filter_criteria = {'file_name': regex}
    if USE_CAPTION_FILTER:
        filter_criteria = {'$or': [filter_criteria, {'caption': regex}]}

    if MULTIPLE_DATABASE:
        total_results = await col.count_documents(filter_criteria) + await sec_col.count_documents(filter_criteria)
        files = []
        async for f in col.find(filter_criteria):
            files.append(f)
        async for f in sec_col.find(filter_criteria):
            files.append(f)
    else:
        total_results = await col.count_documents(filter_criteria)
        files = []
        async for f in col.find(filter_criteria):
            files.append(f)

    return files, total_results


async def get_file_details(query):
    result = await col.find_one({'file_id': query})
    if not result:
        result = await sec_col.find_one({'file_id': query})
    return result


def encode_file_id(s: bytes) -> str:
    r = b""
    n = 0
    for i in s + bytes([22]) + bytes([4]):
        if i == 0:
            n += 1
        else:
            if n:
                r += b"\x00" + bytes([n])
                n = 0
            r += bytes([i])
    return base64.urlsafe_b64encode(r).decode().rstrip("=")


def unpack_new_file_id(new_file_id):
    """Return file_id"""
    decoded = FileId.decode(new_file_id)
    file_id = encode_file_id(
        pack(
            "<iiqq",
            int(decoded.file_type),
            decoded.dc_id,
            decoded.media_id,
            decoded.access_hash
        )
    )
    return file_id
