from allauth.account.adapter import DefaultAccountAdapter

class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=False)
        # 회원가입 폼에서 넘어온 nickname 저장
        data = form.cleaned_data
        user.nickname = data.get('nickname')
        user.save()
        return user