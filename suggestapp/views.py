
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import render
import re
from .models import article, keyword, reader_keyword, reader
import hashlib
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_text
from django.db import IntegrityError
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from .tokens import activation_token
from django.utils import six
from itertools import chain
from django.http import JsonResponse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


from .forms import readerForm


def index(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        activation = 'Activation Link Sent'
        keywords = request.POST.getlist('keywords')
        current_site = get_current_site(request)
        confirmation = False
        if reader.objects.filter(email__iexact=email).exists():
            failure = "The subscription is already requested"
            return render(request, 'suggestapp/index.html', {'failure': failure})
        else:
            token = activation_token.make_token(email)
            hash = hashlib.sha256(str(email).encode('utf-8')).hexdigest()
            db = reader(email=email, state=activation,
                        confirmation=confirmation, token=token, hashId=hash)
            db.save()
            object = reader_keyword.objects.create(readers=email)
            for key in keywords:
                print(key)
                keyw = keyword.objects.get(keyword_name=key)
                object.keywords.add(keyw)
            message = render_to_string('suggestapp/activation_request.html', {
                'email': email,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(email)),
                # method will generate a hash value with user related data
                # 'token': default_token_generator.make_token(email),
                'token': token,
            })

            mailSend = EmailMessage(
                'Please Activate Your Account',
                message,
                settings.EMAIL_HOST_USER,
                [email],
            )
            mailSend.fail_silently = False
            mailSend.send()
            return redirect('suggestapp:activation_sent')
    else:
        form = readerForm()
    return render(request, 'suggestapp/index.html', {'form': form})


def activation_sent_view(request):
    return render(request, 'suggestapp/activation_sent.html')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        readerCheck = reader.objects.get(email=uid)
        tokenCheck = reader.objects.get(token=token)
        current_site = get_current_site(request)
    except:
        readerCheck = None
        tokenCheck = None
    if readerCheck is not None and tokenCheck is not None:
        activated = "Activated"
        confirmation = True
        reader.objects.filter(email=uid).update(
            confirmation=confirmation, state=activated)
        if reader.objects.filter(state=activated):
            articles = reader_keyword.objects.filter(
                readers=uid).values('keywords')
            selectedKeywords = []
            for i in articles:
                query = keyword.objects.filter(
                    keyword_id=i['keywords']).values('keyword_name')
                for a in query:
                    selectedKeywords.append(a['keyword_name'])
            if (len(selectedKeywords)) != 0:
                articlesSend = return_articles(selectedKeywords, uid)
                message = render_to_string('suggestapp/articles.html', {
                    'email': uid,
                    'uidb64': uidb64,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(uid)),
                    'token': token,
                    'articles': articlesSend
                })
                mailSend = EmailMessage(
                    'New Articles for you!',
                    message,
                    settings.EMAIL_HOST_USER,
                    [uid],
                )
                mailSend.fail_silently = False
                mailSend.send()
            else:
                pass

        return render(request, 'suggestapp/activation_success.html')

    if readerCheck is None or tokenCheck is None:
        failure = "Token is invalid"
        return render(request, 'suggestapp/activation_done.html', {'failure': failure})
    # except (TypeError, ValueError, OverflowError):
    # if reader.objects.filter(confirmation=True):
    #     failure = "You have already activated your account"
    #     return render(request, 'suggestapp/activation_done.html', {'failure': failure})
    else:
        return render(request, 'suggestapp/activation_done.html')


def return_articles(selectedKeywords, uid):
    querylist = []
    for element in selectedKeywords:
        query_returned = article.objects.filter(
            term=element).values('term', 'abstract', 'title', 'no')[0:4]
        querylist.append(query_returned)
    returned_articles = list(chain(*querylist))
    return returned_articles


def unsubscribe(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        tokenCheck = reader.objects.get(token=token)
    except:
        tokenCheck = None
    if reader.objects.filter(email=uid).exists() and tokenCheck is not None:
        if request.method == 'POST':
            unsubscribed = "Unsubscribed"
            reader.objects.filter(email=uid).update(state=unsubscribed)
            return render(request, 'suggestapp/unsubscribe.html', {'unsubscribed': unsubscribed})
        else:
            check = "Are you sure to unsubscribe?"
            return render(request, 'suggestapp/unsubscribe.html', {'check': check, 'uid': uid})
    else:
        print('The email does not exist')
        return render(request, 'suggestapp/unsubscribe.html')


def manage(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        tokenCheck = reader.objects.get(token=token)
    except:
        tokenCheck = None
    keywords = reader_keyword.objects.filter(
        readers__iexact=uid).values('keywords')
    keyword_list = []
    for i in keywords:
        key = i['keywords']
        keywords = keyword.objects.filter(
            keyword_id=key).values('keyword_name')
        for s in keywords:
            keyword_list.append(s['keyword_name'])
    text = request.GET.get('li_text')
    keyw = keyword.objects.filter(
        keyword_name=text).values('keyword_id')
    all = keyword.objects.all().values('keyword_name')
    if reader.objects.filter(email=uid).exists() and tokenCheck is not None:
        print("yes")
        for one in keyw:
            tobedeleted = one['keyword_id']
            object = reader_keyword.objects.get(readers=uid)
            object.keywords.remove(tobedeleted)
        if request.method == 'POST':
            keywordSelected = request.POST.getlist('keywords')
            keyw = keyword.objects.filter(
                keyword_name__in=keywordSelected).values('keyword_id')
            for i in keyw:
                key = i['keyword_id']
                object = reader_keyword.objects.get(readers=uid)
                object.keywords.add(key)
            updated = "Your selections are updated."
            return render(request, 'suggestapp/manage.html', {'updated': updated})
        else:
            return render(request, 'suggestapp/manage.html', {'all': all, 'keyword_list': keyword_list})
    else:
        failure = "The account you entered is not the same."
        return render(request, 'suggestapp/manage.html', {'failure': failure})


def article_view(request, no, uidb64):
    articles = article.objects.filter(
        no=no).values()
    if request.is_ajax():
        for elem in articles.values('term'):
            term = elem['term']
        for item in articles.values('vectorized'):
            liked = item['vectorized']
        compared = return_vectorized(liked, term)
        context = {

        }
        return JsonResponse(data=context)
    return render(request, 'suggestapp/article_view.html', {'articles': articles})


def return_vectorized(liked, term):
    other_articles = []
    for elem in article.objects.filter(term=term).values('vectorized'):
        other_articles.append(elem['vectorized'])
    vectorizer = TfidfVectorizer()
    vectorA = vectorizer.fit_transform([liked])
    result = {}
    for item in other_articles:
        vectorB = vectorizer.transform([item])
        similar = cosine_similarity(vectorA, vectorB)
        clear = list(map(float, similar))
        similar = clear[0]
        result[item] = similar
    result = dict((k, v) for k, v in result.items()
                  if v >= 0.5)
    if len(result) > 3:
        threeitems = {A: N for (A, N) in [x for x in result.items()][:3]}
        getDoi = []
        for element in threeitems:
            doiSet = article.objects.filter(vectorized=element).values('doi')
            for i in doiSet:
                getDoi.append(i['doi'])
        doiList = getDoi
        print(doiList)
    else:
        retrieve_new_articles(term)

    # result = sorted(result, key=result.get, reverse=True)
    # print(result)
    # print(vectorA)
    # print(cosine_similarity(vectorA, vectorB))

    return vectorA


def retrieve_new_articles(term):
    retrieved = term
    return retrieved
