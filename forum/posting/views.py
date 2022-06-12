import os
from django.db.models import Q
from django.http import JsonResponse
from django.http import FileResponse
from django.views.decorators.csrf import csrf_exempt
from .models import *


@csrf_exempt
def publish(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    user = User.objects.get(username=request.META.get('HTTP_USERNAME'))
    if user.is_banned:
        return JsonResponse({'errno': 400007, 'msg': '用户已被禁言'})
    sectors = Sector.objects.filter(sector_name=request.POST.get('sector_name'))
    if not sectors.exists():
        return JsonResponse({'errno': 400001, 'msg': '板块不存在'})
    sector = sectors.first()
    title = request.POST.get('title')
    if title is None or title == "":
        return JsonResponse({'errno': 400002, 'msg': '帖子标题为空'})
    content = request.POST.get('content')
    if content is None or content == "":
        return JsonResponse({'errno': 400003, 'msg': '帖子内容为空'})
    time = request.POST.get('time')
    time = checkTime(str(time))
    authority = request.POST.get('authority')
    if int(authority) > user.user_level:
        return JsonResponse({'errno': 400010, 'msg': '发帖权限不能高于用户等级！'})
    posting = Posting(user_id=user, sector_name=sector, title=title, content=content, time=time,
                      recent_comment_time=time, authority=authority)
    posting.save()
    has_file = request.POST.get("has_file")
    if has_file == "true":
        file_id = request.POST.get("file_id")
        file = File.objects.get(file_id=file_id)
        file.posting_id = posting
        file.save()
    user.user_level = updateUserLevel(user.user_experience + 5)
    user.user_experience += 5
    user.save()
    return JsonResponse({'errno': 0, 'msg': '帖子发布成功'})


@csrf_exempt
def uploadFile(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    file = request.FILES.get("in_file")
    filename_raw = file.name
    (filename, filelast) = os.path.splitext(filename_raw)
    myfile = File(filename=filename_raw)
    myfile.save()
    file_newname = str(myfile.file_id) + filelast
    destination = open("media/files/{name}".format(name=file_newname), 'wb+')
    for chunk in file.chunks():
        destination.write(chunk)
    destination.close()
    return JsonResponse({'errno': 0, 'msg': '文件上传成功', 'file_id': myfile.file_id})


@csrf_exempt
def comment(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    user = User.objects.get(username=request.META.get('HTTP_USERNAME'))
    if user.is_banned:
        return JsonResponse({'errno': 400007, 'msg': '用户已被禁言'})
    judge = int(request.POST.get('judge'))
    postings = Posting.objects.filter(posting_id=request.POST.get('posting_id'))
    if not postings.exists():
        return JsonResponse({'errno': 400004, 'msg': '帖子不存在'})
    posting = postings.first()
    reply_dst = None
    reply_dst1 = None
    if not judge == 1:
        reply_id = int(request.POST.get('reply_id'))
        replys = Reply.objects.filter(reply_id=reply_id)
        if not replys.exists():
            return JsonResponse({'errno': 400005, 'msg': '评论不存在'})
        reply_dst = replys.first()
        if judge == 3:
            reply_id1 = int(request.POST.get('reply_id1'))
            replys1 = Reply.objects.filter(reply_id=reply_id1)
            if not replys1.exists():
                return JsonResponse({'errno': 400005, 'msg': '评论不存在'})
            reply_dst1 = replys1.first()
    content = request.POST.get('content')
    if content is None or content == "":
        return JsonResponse({'errno': 400008, 'msg': '回复内容为空'})
    time = request.POST.get('time')
    time = checkTime(str(time))
    reply = Reply(user_id=user, judge=judge, posting_id=posting, content=content, time=time)
    reply.save()
    if judge != 1:
        reply.reply1_id = reply_dst
    if judge == 3:
        reply.reply2_id = reply_dst1
    reply.save()
    posting.recent_comment_time = time
    posting.recent_comment_id = int(reply.reply_id)
    posting.save()
    user.user_level = updateUserLevel(user.user_experience + 2)
    user.user_experience += 2
    user.save()
    return JsonResponse({'errno': 0, 'msg': '评论发表成功'})


@csrf_exempt
def like(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    user = User.objects.get(username=request.META.get('HTTP_USERNAME'))
    judge = int(request.POST.get('judge'))
    j = 0
    if judge == 1:
        postings = Posting.objects.filter(posting_id=int(request.POST.get('posting_id')))
        if not postings.exists():
            return JsonResponse({'errno': 400004, 'msg': '帖子不存在'})
        posting = postings.first()
        user0 = User.objects.filter(posting__posting_id=posting.posting_id).first()
        if Posting.objects.filter(posting_id=posting.posting_id, like=user).exists():
            posting.like_count -= 1
            posting.like.remove(user)
            j = 1
        else:
            posting.like_count += 1
            posting.like.add(user)
        posting.save()
    else:
        replys = Reply.objects.filter(reply_id=int(request.POST.get('reply_id')))
        if not replys.exists():
            return JsonResponse({'errno': 400005, 'msg': '评论不存在'})
        reply = replys.first()
        user0 = User.objects.filter(reply__reply_id=reply.reply_id).first()
        if Reply.objects.filter(reply_id=reply.reply_id, like=user).exists():
            reply.like_count -= 1
            reply.like.remove(user)
            j = 1
        else:
            reply.like_count += 1
            reply.like.add(user)
        reply.save()
    user0.user_level = updateUserLevel(user0.user_experience + 1)
    user0.user_experience += 1
    user0.save()
    if j == 1:
        return JsonResponse({'errno': 0, 'msg': '取消点赞成功', 'type': j})
    else:
        return JsonResponse({'errno': 0, 'msg': '点赞成功', 'type': j})


@csrf_exempt
def searchPosting(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    search = request.POST.get('search')
    postings = \
        Posting.objects.filter(Q(title__icontains=search) | Q(content__icontains=search)).all().order_by('-posting_id')
    if not postings.exists():
        return JsonResponse({'errno': 200008, 'msg': '符合条件的搜索结果为空'})
    data = []
    for posting in postings:
        data.append({
            'posting_id': posting.posting_id,
            'posting_title': posting.title,
            'username': User.objects.filter(posting__posting_id=posting.posting_id).first().username,
            'posting_time': posting.time,
            'like_count': posting.like_count,
            'comment_count': int(posting.reply_set.all().count()),
            'click_count': posting.click_count,
            'recent_comment_time': posting.recent_comment_time,
            'authority': int(posting.authority),
            'has_file': File.objects.filter(posting_id=posting.posting_id).exists(),
            'user_level': User.objects.filter(posting__posting_id=posting.posting_id).first().user_level
        })
    return JsonResponse({'errno': 0, 'data': data})


@csrf_exempt
def deletePosting(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    postings = Posting.objects.filter(posting_id=request.POST.get('posting_id'))
    if not postings.exists():
        return JsonResponse({'errno': 400004, 'msg': '帖子不存在'})
    posting = postings.first()
    posting.delete()
    return JsonResponse({'errno': 0, 'msg': '帖子删除成功'})


@csrf_exempt
def deleteComment(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    replys = Reply.objects.filter(reply_id=request.POST.get('reply_id'))
    if not replys.exists():
        return JsonResponse({'errno': 400005, 'msg': '评论不存在'})
    reply = replys.first()
    reply.delete()
    return JsonResponse({'errno': 0, 'msg': '评论删除成功'})


@csrf_exempt
def getHomepagePostingList(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    posting = Posting.objects.get(posting_id=1)
    data1 = [{
        'posting_id': posting.posting_id,
        'posting_title': posting.title,
        'username': User.objects.filter(posting__posting_id=posting.posting_id).first().username,
        'posting_time': posting.time,
        'like_count': posting.like_count,
        'comment_count': int(posting.reply_set.all().count()),
        'click_count': posting.click_count,
        'recent_comment_time': posting.recent_comment_time,
        'authority': int(posting.authority),
        'has_file': File.objects.filter(posting_id=posting.posting_id).exists()
    }]
    postings1 = Posting.objects.all().order_by('-click_count')
    i = 1
    for posting in postings1:
        if i > 10:
            break
        if int(posting.posting_id) == 1:
            continue
        data1.append({
            'posting_id': posting.posting_id,
            'posting_title': posting.title,
            'username': User.objects.filter(posting__posting_id=posting.posting_id).first().username,
            'posting_time': posting.time,
            'like_count': posting.like_count,
            'comment_count': int(posting.reply_set.all().count()),
            'click_count': posting.click_count,
            'recent_comment_time': posting.recent_comment_time,
            'authority': int(posting.authority),
            'has_file': File.objects.filter(posting_id=posting.posting_id).exists()
        })
        i += 1
    data2 = []
    postings2 = Posting.objects.all().order_by('-posting_id')
    i = 1
    for posting in postings2:
        if i > 10:
            break
        if int(posting.posting_id) == 1:
            continue
        data2.append({
            'posting_id': posting.posting_id,
            'posting_title': posting.title,
            'username': User.objects.filter(posting__posting_id=posting.posting_id).first().username,
            'posting_time': posting.time,
            'like_count': posting.like_count,
            'comment_count': int(posting.reply_set.all().count()),
            'click_count': posting.click_count,
            'recent_comment_time': posting.recent_comment_time,
            'authority': int(posting.authority),
            'has_file': File.objects.filter(posting_id=posting.posting_id).exists()
        })
        i += 1
    sector_data = []
    sectors = ["campus", "discussion", "exercise", "recommendation", "resource"]
    i = 0
    while i < 5:
        mid_sector = sectors[i]
        mid_postings = Posting.objects.filter(sector_name=mid_sector).order_by('-posting_id')
        mid_data = []
        if mid_postings.exists():
            mid_posting = mid_postings.first()
            mid_data.append(True)
            mid_data.append({
                'posting_id': mid_posting.posting_id,
                'posting_title': mid_posting.title,
                'username': User.objects.filter(posting__posting_id=mid_posting.posting_id).first().username,
                'posting_time': mid_posting.time,
                'like_count': mid_posting.like_count,
                'comment_count': int(mid_posting.reply_set.all().count()),
                'click_count': mid_posting.click_count,
                'recent_comment_time': mid_posting.recent_comment_time,
                'authority': int(posting.authority),
                'has_file': File.objects.filter(posting_id=posting.posting_id).exists()
            })
        else:
            mid_data.append(False)
        sector_data.append(mid_data)
        i += 1
    return JsonResponse({
        'errno': 0,
        'data1': data1,
        'data2': data2,
        'campus': sector_data[0],
        'discussion': sector_data[1],
        'exercise': sector_data[2],
        'recommendation': sector_data[3],
        'resource': sector_data[4]
    })


@csrf_exempt
def getSectorPostingList(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    sectors = Sector.objects.filter(sector_name=request.POST.get('sector_name'))
    if not sectors.exists():
        return JsonResponse({'errno': 400001, 'msg': '板块不存在'})
    sector = sectors.first()
    posting_list = sector.posting_set.all().order_by('-recent_comment_id')
    if not posting_list.exists():
        return JsonResponse({'errno': 400006, 'msg': '该板块暂无帖子'})
    posting = Posting.objects.get(posting_id=1)
    data = [{
        'posting_id': posting.posting_id,
        'posting_title': posting.title,
        'username': User.objects.filter(posting__posting_id=posting.posting_id).first().username,
        'posting_time': posting.time,
        'like_count': posting.like_count,
        'comment_count': int(posting.reply_set.all().count()),
        'click_count': posting.click_count,
        'recent_comment_time': posting.recent_comment_time,
        'authority': int(posting.authority),
        'has_file': File.objects.filter(posting_id=posting.posting_id).exists(),
        'user_level': User.objects.filter(posting__posting_id=posting.posting_id).first().user_level
    }]
    for posting in posting_list:
        if posting.posting_id == 1:
            continue
        data.append({
            'posting_id': posting.posting_id,
            'posting_title': posting.title,
            'username': User.objects.filter(posting__posting_id=posting.posting_id).first().username,
            'posting_time': posting.time,
            'like_count': posting.like_count,
            'comment_count': int(posting.reply_set.all().count()),
            'click_count': posting.click_count,
            'recent_comment_time': posting.recent_comment_time,
            'authority': int(posting.authority),
            'has_file': File.objects.filter(posting_id=posting.posting_id).exists(),
            'user_level': User.objects.filter(posting__posting_id=posting.posting_id).first().user_level
        })
    return JsonResponse({
        'errno': 0,
        'sector_name': sector.sector_name,
        'sector_introduction': sector.sector_introduction,
        'data': data
    })


@csrf_exempt
def getUserPostingList(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    user = User.objects.get(username=request.META.get('HTTP_USERNAME'))
    posting_list = user.posting_set.all().order_by('-posting_id')
    data = []
    likes = 0
    for posting in posting_list:
        likes += int(posting.like_count)
        data.append({
            'posting_id': posting.posting_id,
            'posting_title': posting.title,
            'sector_name': Sector.objects.filter(posting__posting_id=posting.posting_id).first().sector_name,
            'posting_time': posting.time,
            'like_count': posting.like_count,
            'comment_count': int(posting.reply_set.all().count()),
            'click_count': posting.click_count,
            'recent_comment_time': posting.recent_comment_time
        })
    return JsonResponse({
        'errno': 0,
        'posting_count': int(posting_list.all().count()),
        'like_count': likes,
        'data': data
    })


@csrf_exempt
def getPostingInfo(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    user = User.objects.get(username=request.META.get('HTTP_USERNAME'))
    posting_id = int(request.POST.get('posting_id'))
    postings = Posting.objects.filter(posting_id=posting_id)
    if not postings.exists():
        return JsonResponse({'errno': 400004, 'msg': '帖子不存在'})
    posting = postings.first()
    replys = posting.reply_set.all().filter(judge=1)
    data = []
    for reply in replys:
        replys1 = reply.reply_to1.all()
        data1 = []
        for reply1 in replys1:
            user2 = User.objects.filter(reply__reply_id=reply1.reply_id).first()
            data2 = {
                'reply_id': reply1.reply_id,
                'user_id': user2.userid,
                'username': user2.username,
                'user_level': user2.user_level,
                'user_photo': user2.photo.url,
                'content': reply1.content,
                'like_count': reply1.like_count,
                'time': reply1.time,
                'judge': reply1.judge,
                'like': user.like_reply.filter(reply_id=reply1.reply_id).exists()
            }
            if reply1.judge == 3:
                mid_reply = Reply.objects.filter(reply_to2__reply_id=reply1.reply_id).first()
                data2['reply_to'] = User.objects.get(reply__reply_id=mid_reply.reply_id).username
            data1.append(data2)
        user1 = User.objects.filter(reply__reply_id=reply.reply_id).first()
        data.append({
            'reply_id': reply.reply_id,
            'user_id': user1.userid,
            'username': user1.username,
            'user_level': user1.user_level,
            'user_photo': user1.photo.url,
            'content': reply.content,
            'like_count': reply.like_count,
            'reply_count': replys1.count(),
            'time': reply.time,
            'like': user.like_reply.filter(reply_id=reply.reply_id).exists(),
            'replys': data1
        })
    user0 = User.objects.filter(posting__posting_id=posting.posting_id).first()
    return_data = {
        'errno': 0,
        'posting_title': posting.title,
        'posting_time': posting.time,
        'sector_name': Sector.objects.filter(posting__posting_id=posting.posting_id).first().sector_name,
        'user_id': user0.userid,
        'username': user0.username,
        'user_level': user0.user_level,
        'user_photo': user0.photo.url,
        'content': posting.content,
        'like_count': posting.like_count,
        'authority': int(posting.authority),
        'reply_count': replys.count(),
        'like': user.like_posting.filter(posting_id=posting.posting_id).exists(),
        'replys': data,
        'has_file': File.objects.filter(posting_id=posting.posting_id).exists(),
        'my_user_level': user.user_level

    }
    if File.objects.filter(posting_id=posting.posting_id).exists():
        return_data['resource'] = File.objects.get(posting_id=posting.posting_id).filename
    posting.click_count += 1
    posting.save()
    return JsonResponse(return_data)


@csrf_exempt
def downloadFile(request):
    posting_id = int(request.POST.get('posting_id'))
    postings = Posting.objects.filter(posting_id=posting_id)
    if not postings.exists():
        return JsonResponse({'errno': 400004, 'msg': '帖子不存在'})
    posting = postings.first()
    files = File.objects.filter(posting_id=posting.posting_id)
    if not files.exists():
        return JsonResponse({'errno': 400009, 'msg': '当前帖子无文件资源'})
    file = posting.file_set.filter().first()
    filename_raw = file.filename
    print(filename_raw.encode('utf-8'))
    (filefirst, filelast) = os.path.splitext(filename_raw)
    filename = str(file.file_id) + filelast
    file_main = FileResponse(open("media/files/{name}".format(name=filename), 'rb'), as_attachment=True,
                             filename=filename_raw)
    return file_main


def updateUserLevel(in_experience):
    if in_experience < 5:
        return 0
    elif 5 <= in_experience < 10:
        return 1
    elif 10 <= in_experience < 20:
        return 2
    elif 20 <= in_experience < 50:
        return 3
    elif 50 <= in_experience < 100:
        return 4
    elif 100 <= in_experience < 200:
        return 5
    elif 200 <= in_experience < 500:
        return 6
    elif 500 <= in_experience < 1000:
        return 7
    elif 1000 <= in_experience < 2000:
        return 8
    elif 2000 <= in_experience < 5000:
        return 9
    else:
        return 10


def checkTime(in_time):
    year0 = (in_time.split(" "))[0]
    time0 = (in_time.split(" "))[1]
    if "上午" in time0:
        time0 = time0[2:]
    if "下午" in time0:
        time0 = time0[2:]
        time1 = (time0.split(":"))[0]
        time_mid = int(time1) + 12
        time1 = str(time_mid)
        time0 = time1 + ":" + (time0.split(":"))[1] + ":" + (time0.split(":"))[2]
    return year0 + " " + time0
