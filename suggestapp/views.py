
from .forms import readerForm
from datetime import datetime
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import render
import re
from .models import article, keyword, reader_keyword, reader, reader_like
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
import requests
import json
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
nltk.download('punkt')
nltk.download('stopwords')


def index(request):
    # Index gets the data of reader, saves the database, sends to activation.
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
        # This checks if activation token is valid. After the activation, new articles are send, and saved to database.
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
                print(articlesSend)
                doiList = []
                for i in articlesSend:
                    doiList.append(i['doi'])
                term = article.objects.filter(
                    doi__in=doiList).values('term', 'doi')
                for elem in term:
                    send = "Sent"
                    sent = reader_like(reader=uid, state=send,
                                       term=elem['term'], doi=elem['doi'])
                    sent.save()
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
      # Only return articles for the mails after activation.
    querylist = []
    for element in selectedKeywords:
        query_returned = article.objects.filter(
            term=element).values('term', 'abstract', 'title', 'no', 'doi')[0:5]
        querylist.append(query_returned)
    returned_articles = list(chain(*querylist))
    return returned_articles


def unsubscribe(request, uidb64, token):
     # Unsubscibe is happening as updating the state of the reader.
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
    # Checks tokens, updates the keywords selected before. It is achieved with Ajax.
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
      # It helps to see articles and Ajax is used.
    email = force_text(urlsafe_base64_decode(uidb64))
# Article on UI
    articles = article.objects.filter(
        no=no).values()
# If the article is liked or directed to link
    if request.is_ajax():
        for i in articles:
            like = "Liked"
            print(i['doi'])
            reader_like.objects.filter(reader=email, doi=i['doi']).update(
                reader=email, state=like,
                term=i['term'], doi=i['doi'])
        context = {
        }
        return JsonResponse(data=context)

    return render(request, 'suggestapp/article_view.html', {'articles': articles})


def trigger(request):
    current_site = get_current_site(request)
    readers = reader.objects.all().values('email')
    readerList = []
    for element in readers:
        readerList.append(element)
    # for i in readerList:
    #     readers = i
    if request.method == 'POST':
        email = request.POST.get('emails')
        compared = return_vectorized(email, current_site)
        if type(compared) == str:
            similarity = "The reader has not liked any articles yet."
            return render(request, 'suggestapp/trigger.html', {'similarity': similarity})
        else:
            return render(request, 'suggestapp/trigger.html', {'readerList': readerList, 'compared': compared})
    else:
        return render(request, 'suggestapp/trigger.html', {'readers': readers, 'readerList': readerList})


def retrieve(request):
    if request.method == 'POST':
        retrieve_new_articles()
        return render(request, 'suggestapp/retrieve.html', )
    else:
        return render(request, 'suggestapp/retrieve.html')


def return_vectorized(email, current_site):
    # It uses NLTK, TF-IDF and calculates the similarities.
    for i in reader.objects.filter(email=email).values('token'):
        token = i['token']
    allLikes = []
    allTerm = []
    dictionary = {}
    try:
        for elem in reader_like.objects.filter(
                reader=email, state__in=['Liked']).values('doi', 'term'):
            allLikes.append(elem['doi'])
            allTerm.append(elem['term'])
        dictionary['term'] = allTerm
        vectorA = []
        for item in article.objects.filter(doi__in=allLikes).values('vectorized'):
            vectorA.append(item['vectorized'])
        vectorA = ' '.join(vectorA)
    # In order not to send same articles to same emails, excludeList implemented.
        excludeList = []
        for element in reader_like.objects.filter(
                reader=email, state__in=['Sent', 'Liked']).values('doi'):
            excludeList.append(element['doi'])
        vectorizer = TfidfVectorizer()
        vectorA = vectorizer.fit_transform([vectorA])
        other_articles = []
        for term in allTerm:
            for elem in article.objects.filter(term=term).exclude(doi__in=excludeList).values('vectorized'):
                other_articles.append(elem['vectorized'])
            result = {}
            for item in other_articles:
                vectorB = vectorizer.transform([item])
                similarity = cosine_similarity(vectorA, vectorB)
                clear = list(map(float, similarity))
                similar = clear[0]
                result[item] = similar
            resultArticles = dict((k, v) for k, v in result.items()
                                  if v >= 0.4)
        if len(resultArticles) > 5:
            fiveitems = {A: N for (A, N) in [x for x in result.items()][:5]}
            doiSet = []
            for element in fiveitems:
                doiSet.append(article.objects.filter(
                    vectorized=element).values('doi'))
            doiList = []
            for all in doiSet:
                for elem in all:
                    doiList.append(elem['doi'])
            articlesSend = article.objects.filter(doi__in=doiList).values(
                'term', 'abstract', 'title', 'no', 'doi')
            send_email(email, articlesSend, current_site, token)
            for i in articlesSend:
                send = "Sent"
                sent = reader_like(reader=email, state=send,
                                   term=i['term'], doi=i['doi'])
                sent.save()
                similarity = similarity
        else:
            pass
    except:
        similarity = "The reader has not liked any articles."

    return similarity


def send_email(email, articlesSend, current_site, token):
    uid = urlsafe_base64_encode(force_bytes(email))
    message = render_to_string('suggestapp/articles_after.html', {
        'email': email,
        'uidb64': uid,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(email)),
        'token': token,
        'articles': articlesSend
    })
    mailSend = EmailMessage(
        'New Articles for you!',
        message,
        settings.EMAIL_HOST_USER,
        [email],
    )
    mailSend.fail_silently = False
    mailSend.send()
    return articlesSend


def retrieve_new_articles():

    list = ['Algorithms', "Artificial Intelligence",
            "Networking", "Wireless Communication", "Data Science", "Molecular Communication", "Computer Science"]
    apiKey = ""
    keywordList = []
    doilist = []
    for item in list:
        url = ("https://api.elsevier.com/content/search/sciencedirect?query=" +
               item+"&apiKey=&count=5&date=2022")
        response = requests.request("GET", url)
        result = json.loads(response.text.encode(
            'utf-8'))
        if 'search-results' in result:
            result = result['search-results']
            if 'entry' in result:
                result = result['entry']
            else:
                pass
        else:
            pass
        for i in result:
            doi = i['prism:doi']
            doilist.append(doi)
            keywordList.append(item)
    dictionary = dict(zip(doilist, keywordList))
    print(doilist)
    for doi in dictionary:
        keyword = dictionary[doi]
    dois = []
    for i in article.objects.filter(doi=doi).values('doi'):
        dois.append(i['doi'])
    new_list = [a for a in doilist if (a not in dois)]
    # print(new_list)
    # for item in article.objects.filter(doi__in=doilist).exclude(doi__in=dois).values:
    for doi in new_list:
        url = ("https://api.elsevier.com/content/article/doi/"+doi+"?apiKey="+apiKey+"&httpAccept=application/json"
               )
        response = requests.request("GET", url)
        result = json.loads(response.text.encode(
            'utf-8'))['full-text-retrieval-response']['coredata']
        if result['dc:description'] != None:
            abstract = result['dc:description']
            lowerCase = abstract.lower()
            text_tokens = word_tokenize(lowerCase)
            stops = set(stopwords.words('english'))
            tokens_without_sw = [
                word for word in text_tokens if not word in stops]
            noStop = ' '.join(tokens_without_sw)
            tokenizer = nltk.RegexpTokenizer(r"\w+")
            new_words = tokenizer.tokenize(noStop)
            wordsFiltered = " ".join(new_words)
            vectorizer = TfidfVectorizer()
            vectors = vectorizer.fit_transform([wordsFiltered])
            feature_names = vectorizer.get_feature_names()
            dense = vectors.todense()
            denselist = dense.tolist()
            for part in denselist:
                dense = part
            tfidResults = {feature_names[part]: dense[part]
                           for part in range(len(feature_names))}
            vectorized = " ".join(tfidResults)
            author = []
            if result['dc:creator'] == None:
                pass
            else:
                res = result['dc:creator']
                if type(res) == dict:
                    authors = result['dc:creator']['$']
                else:
                    for auth in result['dc:creator']:
                        author.append(auth['$'])
                        authors = (',').join(author)
            doiSave = result['prism:doi']
            date = result['prism:coverDate']
            link = result['link'][1]['@href']
            title = result['dc:title']
        try:
            if article.objects.get(doi=doiSave) != None:
                pass

        except:
            print("saved")
            articles_retrieved = article(doi=doiSave, title=title, authors=authors,
                                         abstract=abstract, term=keyword, date=date, link=link, vectorized=vectorized)
            articles_retrieved.save()

    return new_list
