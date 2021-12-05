from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import render
import re
# from .forms import UserForm
from .models import topicname, reader
import hashlib

from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_text
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from .tokens import activation_token
from django.template.loader import render_to_string
from django.utils import six

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
            db = reader(email=email, keywords=keywords,
                        state=activation, confirmation=confirmation, token=token, hashId=hash)
            db.save()

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
    # print(request)
    # print(token)
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        readerCheck = reader.objects.get(email=uid)
        tokenCheck = reader.objects.get(token=token)
        print(tokenCheck)
        # confirmationCheck = reader.objects.filter(
        #     email=uid).values('confirmation')
    except:
        readerCheck = None
        tokenCheck = None
    if readerCheck is not None and tokenCheck is not None:
        activated = "Activated"
        confirmation = True
        reader.objects.filter(email=uid).update(
            confirmation=confirmation, state=activated)
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
    keywords = reader.objects.filter(
        email__iexact=uid).values('keywords')
    # print(keywords)
    # for i in keywords:
    #     keys = (i['keywords'])
    # for a in keys:
    #     print(a)

    email = request.POST.get('email')
    keywordSelected = request.POST.getlist('keywords')
    if request.method == 'POST':
        if email == uid and tokenCheck is not None:
            reader.objects.filter(email=uid).update(
                keywords=keywordSelected)
            updated = "Your selections are updated."
            return render(request, 'suggestapp/manage.html', {'updated': updated})
        else:
            failure = "The account you entered is not the same."
            return render(request, 'suggestapp/manage.html', {'failure': failure})

    form = readerForm()
    return render(request, 'suggestapp/manage.html', {'form': form, 'keywords': keywords})


# def index(request):
#     form = UserRegisterForm()
#     return render(request, 'suggestapp/index.html', {'form': form})
# if request.method == 'POST':
# user_form = UserRegisterForm(request.POST)
# if user_form.is_valid():
#     email = user_form.cleaned_data.get('email')
#     new_user = User.objects.create(
#         email=email)
#     new_user = user_form.save(commit=False)
# # new_user.set_password(password) # hashes the password
#     new_user.is_active = False
#     new_user.save()
# # current_site = get_current_site(request)
# # message = render_to_string('email_activation_link.html', {
# #     'new_user': new_user,
# #     'domain': current_site.domain,
# #     'uid': urlsafe_base64_encode(force_bytes(new_user.pk)),
# #     'token': account_activation_token.make_token(new_user),
# # })
# # mail_subject = 'Activate your Frac account.'
# #to_email = form.cleaned_data.get('email')
#     email = user_form.cleaned_data.get('email')
# to_email = EmailMessage(mail_subject, message,
#                         to=[email])  # [to_email])
# to_email.send()
# return render(request, 'suggestapp/index.html', {'user_form': user_form})
# else:
#     return render(request, 'suggestapp/index.html')
# def index(request):
#     registered = False
#     result = topicname.objects.all()
#     if request.method == 'POST':
#         user_form = UserForm(data=request.POST)
#         if user_form.is_valid():
#             # Save User Form to Database
#             user = user_form.save()
#             # # Hash the password
#             # user.set_password(user.password)
#             # # Store with Hashed password
#             user.save()
#             # Registration success
#             registered = True
#             return render(request, 'suggestapp/index.html')

#     else:
#         # is not an HTTP post so give forms as blank
#         user_form = UserForm()
#         # email = request.POST.get('email')
#         # if request.POST.get('keywords'):
#         #     keywords = request.POST.getlist('keywords')
#         #     db = subscriber(email=email, keywords=keywords)
#         #     db.save()
#         #     registered = True
#         #     key = (", ".join(keywords))

#         #     mailSend = EmailMessage(
#         #         'Thank you for subscribing.Following topics will be shared with you!',
#         #         key,
#         #         settings.EMAIL_HOST_USER,
#         #         [email],
#         #     )
#         #     mailSend.fail_silently = False
#         #     mailSend.send()

#         # savedata = subscriber()
#         # savedata.keywords = request.POST.get('keywords')
#         # savedata.save()
#         return render(request, 'suggestapp/index.html',
#                       {'user_form': user_form,
#                        'registered': registered})


# def index(request):
#     registered = False
#     result = topicname.objects.all()
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         if request.POST.get('keywords'):
#             keywords = request.POST.getlist('keywords')
#             db = subscriber(email=email, keywords=keywords)
#             db.save()
#             registered = True
#             key = (", ".join(keywords))

#             mailSend = EmailMessage(
#                 'Thank you for subscribing.Following topics will be shared with you!',
#                 key,
#                 settings.EMAIL_HOST_USER,
#                 [email],
#             )
#             mailSend.fail_silently = False
#             mailSend.send()

#             # savedata = subscriber()
#             # savedata.keywords = request.POST.get('keywords')
#             # savedata.save()
#             return render(request, 'suggestapp/index.html',
#                           {'result': result, 'registered': registered, 'keywords': keywords})

#     else:
#         return render(request, 'suggestapp/index.html',
#                       {'result': result})
