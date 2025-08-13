from django.http import JsonResponse


def response_dict(code : int = 0, message : str = "", data : dict|list = None):
    return JsonResponse({
        "code": code,
        "message": message,
        "data": data,
    })

# 获取第一个错误信息
def get_first_error(form):
    first_error = next(iter(form.errors.items()))
    field_name, error_list = first_error
    error_msg = {
        field_name: error_list[0]
    }
    return error_msg