#!/usr/bin/env python
# -*- coding: utf-8 -*-
from app.libs.redprint import Redprint
from app.libs.token_auth import user_auth
from app.libs.error_code import Success200
from app.validators.ios import UpdateDataFileValidatorsForm

obj = "demo"
api = Redprint(obj)


@api.route("/pro", methods=["POST"])
@user_auth.login_required
def ai_pro():
    form = UpdateDataFileValidatorsForm().validate_for_api()
    xxxxx = form.xxxxx.data
    return Success200(data=xxxxx)




