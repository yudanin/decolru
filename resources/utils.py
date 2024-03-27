from django.utils.text import slugify
from .models import Msgs, Langs

# file_upload_folder = '/uploads/'

language_code = 1

langs = {lang.id: lang.lang_name for lang in Langs.objects.all()}

rs = Msgs.objects.filter(page_id__isnull=True, lang_code=language_code) | Msgs.objects.filter(
    lang_code=language_code).values(
    'msg_name', 'description')
msgs = {msg.msg_name: msg.description for msg in rs}


def get_language_code(request):
    language_code = request.session.get("language_code")
    if not language_code:
        language_code = 1
    return language_code


def get_msgs(request):
    language_code = get_language_code(request)
    rs = Msgs.objects.filter(page_id__isnull=True, lang_code=language_code) | Msgs.objects.filter(
        lang_code=language_code).values(
        'msg_name', 'description')
    msgs = {msg.msg_name: msg.description for msg in rs}
    msgs['language_code'] = language_code
    return msgs


# def validate_date_past_or_current(value):
#     if value > timezone.now().date():
#         msgs = get_msgs(self.request)
#         raise ValidationError(_(msgs['validation_past_current_date']), code='invalid_date')


def generate_slug(title):
    # Remove any special characters and convert to lowercase
    cleaned_title = title.lower()
    # Replace Cyrillic characters with their Latin equivalents
    cleaned_title = cleaned_title.replace('а', 'a') \
        .replace('б', 'b') \
        .replace('в', 'v') \
        .replace('г', 'g') \
        .replace('д', 'd') \
        .replace('е', 'e') \
        .replace('ё', 'e') \
        .replace('ж', 'zh') \
        .replace('з', 'z') \
        .replace('и', 'i') \
        .replace('й', 'i') \
        .replace('к', 'k') \
        .replace('л', 'l') \
        .replace('м', 'm') \
        .replace('н', 'n') \
        .replace('о', 'o') \
        .replace('п', 'p') \
        .replace('р', 'r') \
        .replace('с', 's') \
        .replace('т', 't') \
        .replace('у', 'u') \
        .replace('ф', 'f') \
        .replace('х', 'h') \
        .replace('ц', 'c') \
        .replace('ч', 'ch') \
        .replace('ш', 'sh') \
        .replace('щ', 'shch') \
        .replace('ъ', '') \
        .replace('ы', 'y') \
        .replace('ь', '') \
        .replace('э', 'e') \
        .replace('ю', 'yu') \
        .replace('я', 'ya')
    # Use slugify to convert the cleaned title to a slug
    slug = slugify(cleaned_title)
    return slug
