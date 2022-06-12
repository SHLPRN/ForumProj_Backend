import datetime
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from posting.models import Posting, Reply
from user.models import User
from utils.token import create_token


@csrf_exempt
def register(request):
    if request.method == 'POST':
        username = request.POST.get('input_id')
        password_1 = request.POST.get('input_password')
        password_2 = request.POST.get('input_password2')
        users = User.objects.filter(username=username)
        if users.exists():
            return JsonResponse({'errno': 300001, 'msg': '用户名已注册'})
        if password_1 != password_2:
            return JsonResponse({'errno': 300002, 'msg': '两次输入的密码不一致'})
        User.objects.create(username=username, password=password_1, is_admin=False)
        return JsonResponse({'errno': 0, 'msg': '注册成功'})
    else:
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})


@csrf_exempt
def login(request):
    if request.method == 'POST':
        username = request.POST.get('input_id')
        password = request.POST.get('input_password')
        admin_flag = request.POST.get('input_admin_password')
        users = User.objects.filter(username=username)
        if users.exists():
            user = users.first()
            if user.password == password:
                token = create_token(username)
                today = datetime.date.today()
                tmp_last_login_day = user.last_login_day
                if user.is_banned:
                    n = today - user.last_login_day
                    if n.days > 0:
                        mid = n.days
                        if user.ban_time <= n.days:
                            mid = user.ban_time
                            user.is_banned = False
                        user.ban_time -= mid
                        user.last_login_day = today
                        user.save()
                if admin_flag is not None and admin_flag != '':
                    if admin_flag == 'buaa2020':
                        user.is_admin = True
                        user.save()
                    else:
                        return JsonResponse({'errno': 100005, 'msg': '管理员验证码错误，请重新登录'})
                user.last_login_day = today
                user.save()
                return JsonResponse({
                    'errno': 0,
                    'msg': '登录成功',
                    'data': {
                        'username': user.username,
                        'authorization': token,
                        'userid': user.userid,
                        'is_admin': user.is_admin,
                        'photo': user.photo.url,
                        'last_login_day': tmp_last_login_day
                    }
                })
            else:
                return JsonResponse({'errno': 100003, 'msg': '密码错误'})
        else:
            return JsonResponse({'errno': 100004, 'msg': '用户不存在'})
    else:
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})


@csrf_exempt
def modify_username(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    users = User.objects.filter(username=request.META.get('HTTP_USERNAME'))
    if not users.exists():
        return JsonResponse({'errno': 50001, 'msg': '请登录'})
    user = users.first()
    username = request.POST.get('username')
    if username is None or username == '':
        return JsonResponse({'errno': 400001, 'msg': '没有做出修改'})
    users = User.objects.filter(username=username)
    if users.exists():
        return JsonResponse({'errno': 300001, 'msg': '用户名已注册'})
    user.username = username
    user.save()
    token = create_token(username)
    return JsonResponse({'errno': 0, 'msg': '名称修改成功', 'authorization': token, 'username': username})


@csrf_exempt
def modify_photo(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    users = User.objects.filter(username=request.META.get('HTTP_USERNAME'))
    if not users.exists():
        return JsonResponse({'errno': 500001, 'msg': '请登录'})
    user = users.first()
    photo = request.FILES.get('photo', None)
    if photo is None:
        return JsonResponse({'errno': 400001, 'msg': '没有做出修改'})
    user.photo = photo
    user.save()
    return JsonResponse({'errno': 0, 'msg': '图片修改成功', 'photo': user.photo.url})


@csrf_exempt
def ban_user(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})

    users = User.objects.filter(username=request.META.get('HTTP_USERNAME'), is_admin=True)
    if not users.exists():
        return JsonResponse({'errno': 200002, 'msg': '当前用户非管理员身份'})

    ban_time = request.POST.get('ban_time')
    if ban_time is None:
        return JsonResponse({'errno': 200003, 'msg': '未设定禁言时间'})
    banned_username = request.POST.get('banned_username')
    if banned_username is None:
        return JsonResponse({'errno': 200004, 'msg': '未提供用户姓名'})
    banned_users = User.objects.filter(username=banned_username)
    if not banned_users.exists():
        return JsonResponse({'errno': 200005, 'msg': '用户不存在'})
    banned_user = banned_users.first()
    banned_user.ban_time = int(ban_time)
    banned_user.last_login_day = datetime.date.today()
    banned_user.is_banned = True
    banned_user.save()
    return JsonResponse({'errno': 0, 'msg': '用户禁言成功'})


@csrf_exempt
def release_ban(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    users = User.objects.filter(username=request.META.get('HTTP_USERNAME'), is_admin=True)
    if not users.exists():
        return JsonResponse({'errno': 200002, 'msg': '当前用户非管理员身份'})
    banned_username = request.POST.get('banned_username')
    if banned_username is None:
        return JsonResponse({'errno': 200004, 'msg': '未提供用户姓名'})
    banned_users = User.objects.filter(username=banned_username)
    if not banned_users.exists():
        return JsonResponse({'errno': 200005, 'msg': '用户不存在'})
    banned_user = banned_users.first()
    banned_user.ban_time = 0
    banned_user.is_banned = False
    banned_user.save()
    return JsonResponse({'errno': 0, 'msg': '用户解禁成功'})


@csrf_exempt
def delete_posting(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    users = User.objects.filter(username=request.META.get('HTTP_USERNAME'), is_admin=True)
    if not users.exists():
        return JsonResponse({'errno': 200002, 'msg': '当前用户非管理员身份'})
    posting_id = int(request.POST.get('posting_id'))
    postings = Posting.objects.filter(posting_id=posting_id)
    if not postings.exists():
        return JsonResponse({'errno': 400004, 'msg': '帖子不存在'})
    posting = postings.first()
    posting.delete()
    return JsonResponse({'errno': 0, 'msg': '删除帖子成功'})


@csrf_exempt
def create_admin(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    users = User.objects.filter(username=request.META.get('HTTP_USERNAME'), is_admin=True)
    if not users.exists():
        return JsonResponse({'errno': 200002, 'msg': '当前用户非管理员身份'})
    admin_name = request.POST.get('username')
    if admin_name is None:
        return JsonResponse({'errno': 200003, 'msg': '未提供新管理员名称'})
    password = request.POST.get('password')
    if password is None or password == '':
        return JsonResponse({'errno': 200004, 'msg': '未输入密码'})
    User.objects.create(username=admin_name, password=password, is_admin=True)
    return JsonResponse({'errno': 0, 'msg': '新管理员注册成功'})


@csrf_exempt
def modify_password(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    users = User.objects.filter(username=request.META.get('HTTP_USERNAME'))
    if not users.exists():
        return JsonResponse({'errno': 100004, 'msg': '用户不存在'})
    user = users.first()
    password_1 = request.POST.get('password_1')
    password_2 = request.POST.get('password_2')
    if password_1 != password_2:
        return JsonResponse({'errno': 300002, 'msg': '两次输入的密码不一致'})
    user.password = password_1
    user.save()
    return JsonResponse({'errno': 0, 'msg': '修改密码成功'})


@csrf_exempt
def manage(request):
    users = User.objects.filter(username=request.META.get('HTTP_USERNAME'), is_admin=True)
    if not users.exists():
        return JsonResponse({'errno': 200002, 'msg': '当前用户非管理员'})
    page_num = request.POST.get('page', 1)
    users = User.objects.all().values()
    result = User.objects.count()
    paginator = Paginator(users, 20)
    u_page = paginator.page(int(page_num))
    return JsonResponse({'errno': 0, 'user_sum': result, 'page_data': list(u_page)})


@csrf_exempt
def space(request):
    users = User.objects.filter(username=request.META.get('HTTP_USERNAME'))
    if not users.exists():
        return JsonResponse({'errno': 50001, 'msg': '请登录'})
    user = users.first()
    postings = Posting.objects.filter(user_id=user.userid)
    replys = Reply.objects.filter(user_id=user.userid)
    posting_exist_flag = 1
    reply_exist_flag = 1
    if not postings.exists():
        posting_exist_flag = 0
    if not replys.exists():
        reply_exist_flag = 0
    posting_list = list(postings.values())
    reply_list = list(replys.values())
    i = 0
    for posting in postings:
        posting_list[i]['comment_count'] = int(posting.reply_set.all().count())
        i += 1
    i = 0
    for reply in replys:
        mid_posting = Posting.objects.get(reply__reply_id=reply.reply_id)
        reply_list[i]['posting_title'] = mid_posting.title
        i += 1
    return JsonResponse({'errno': 0,
                         'postings': posting_list,
                         'replys': reply_list,
                         'user_level': user.user_level,
                         'user_experience': user.user_experience,
                         'user_photo': user.photo.url,
                         'posting_exist_flag': posting_exist_flag,
                         'reply_exist_flag': reply_exist_flag
                         })


@csrf_exempt
def other_space(request):
    other_name = request.POST.get("other_name")
    users = User.objects.filter(username=other_name)
    if not users.exists():
        return JsonResponse({'errno': 500001, 'msg': '当前查看用户不存在'})
    user = users.first()
    postings = Posting.objects.filter(user_id=user.userid)
    replys = Reply.objects.filter(user_id=user.userid)
    posting_exist_flag = 1
    reply_exist_flag = 1
    if not postings.exists():
        posting_exist_flag = 0
    if not replys.exists():
        reply_exist_flag = 0
    posting_list = list(postings.values())
    reply_list = list(replys.values())
    i = 0
    for posting in postings:
        posting_list[i]['comment_count'] = int(posting.reply_set.all().count())
        i += 1
    i = 0
    for reply in replys:
        mid_posting = Posting.objects.get(reply__reply_id=reply.reply_id)
        reply_list[i]['posting_title'] = mid_posting.title
        i += 1
    return JsonResponse({'errno': 0,
                         'postings': posting_list,
                         'replys': reply_list,
                         'user_level': user.user_level,
                         'user_experience': user.user_experience,
                         'user_photo': user.photo.url,
                         'posting_exist_flag': posting_exist_flag,
                         'reply_exist_flag': reply_exist_flag
                         })


@csrf_exempt
def delete_reply(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    users = User.objects.filter(username=request.META.get('HTTP_USERNAME'), is_admin=True)
    if not users.exists():
        return JsonResponse({'errno': 200002, 'msg': '当前用户非管理员身份'})
    reply_id = int(request.POST.get('reply_id'))
    replys = Reply.objects.filter(reply_id=reply_id)
    if not replys.exists():
        return JsonResponse({'errno': 400004, 'msg': '回复不存在'})
    reply = replys.first()
    reply.delete()
    return JsonResponse({'errno': 0, 'msg': '删除回复成功'})
