from app.imports import *
from app.models import *
from app.ytd import *

app = FastAPI(title="DarkStore Test Task", docs_url="/", redoc_url=None)
JWT_SECRET = 'myjwtsecret'

@app.post('/token', tags=["Started Requirements"])
async def generate_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail='Invalid username or password'
        )

    user_obj = await User_Pydantic.from_tortoise_orm(user)
    token = jwt.encode(user_obj.dict(), JWT_SECRET)
    return {'access_token' : token, 'token_type' : 'bearer'}  

@app.post('/admin', response_model=User_Pydantic, tags=["Started Requirements"])
async def create_admin():
    user_admin = User(username="admin", password_hash=bcrypt.hash("secret"))
    await user_admin.save()
    return await User_Pydantic.from_tortoise_orm(user_admin)

@app.post('/users', response_model=User_Pydantic, tags=["Started Requirements"])
async def create_user(user: UserIn_Pydantic):
    user_obj = User(username=user.username, password_hash=bcrypt.hash(user.password_hash))
    await user_obj.save()
    return await User_Pydantic.from_tortoise_orm(user_obj)

@app.post('/profiles', tags=["User's functions"])        
async def create_profile(profile: ProfileIn_Pydantic, token : str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    current_user_id = payload.get('id')
    profile_obj = await Profile.create(**profile.dict(exclude_unset=True))
    profile_obj.user_id = current_user_id
    return await Profile_Pydantic.from_tortoise_orm(profile_obj)    

@app.patch('/profile', tags=["User's functions"])
async def update_profile_amount(profile_name: str, city: ProfileIn_Pydantic, token : str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    current_user_id = payload.get('id')
    await Profile.filter(name=profile_name).update(**city.dict(exclude_unset=True))
    return await Profile_Pydantic.from_queryset_single(Profile.get(name = profile_name, user_id = current_user_id))    

@app.get('/profiles/', tags=["User's functions"])
async def get_your_profiles(token : str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    current_user_id = payload.get('id')
    return await Profile_Pydantic.from_queryset(Profile.filter(user_id = current_user_id))

@app.delete('/profile/{profile_name}', tags=["User's functions"])
async def delete_profile(profile_name: str, token : str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    current_user_id = payload.get('id')
    await Profile.filter(name=profile_name, user_id = current_user_id).delete()
    return {}

@app.get("/ytd", tags=["YTD"])
async def get_profile_ytd(
    client: finnhub.Client = Depends(finnhub_client), token : str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    current_user_id = payload.get('id')
    profile = await Profile.filter(user_id = current_user_id)
    try:
        performance = sum(profile_performance(client, profile))
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong.",
        )
    return {"performance": performance}

@app.get("/ytd/min-max", response_model=YTDMinMax, tags=["YTD"])
async def get_profile_ytd_min_max(
    client: finnhub.Client = Depends(finnhub_client), token : str = Depends(oauth2_scheme)
):
    payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    current_user_id = payload.get('id')
    profile = await Profile.filter(user_id=current_user_id)
    if len(profile):
        try:
            values = (
                get_currency_values(client, x.name, get_ytd_borders())
                for x in profile
            )
        except:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something went wrong.",
            )
        (min_value, min_value_index), (
            max_value,
            max_value_index,
        ) = get_profile_min_max(values)
        min_date = dt.date(dt.date.today().year, 1, 1) + dt.timedelta(
            days=min_value_index
        )
        max_date = dt.date(dt.date.today().year, 1, 1) + dt.timedelta(
            days=max_value_index
        )
    else:
        min_value = max_value = 0
        min_date = max_date = dt.date.today()
    return {
        "min": {"amount": min_value, "date": min_date},
        "max": {"amount": max_value, "date": max_date},
    }    
    
@app.get('/portfolios', tags=["Admin's Panel"])   
async def get_portfolies(user: User_Pydantic = Depends(get_current_user), token : str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    current_user_username = payload.get('username')
    if current_user_username == "admin":
        return await Profile_Pydantic.from_queryset(Profile.all())

@app.delete('/profiles', tags=["Admin's Panel"])
async def delete_db_of_profiles(token : str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    current_user_username = payload.get('username')
    if current_user_username == "admin":
        await Profile.all().delete()
        return {}    

@app.delete('/users', tags=["Admin's Panel"])
async def delete_db_of_users(token : str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    current_user_username = payload.get('username')
    if current_user_username == "admin":
        await User.all().delete()
        return {}   

register_tortoise(
    app,
    db_url='sqlite://db.sqlite3',
    modules={'models': ['main']},
    generate_schemas=True,
    add_exception_handlers=True
)