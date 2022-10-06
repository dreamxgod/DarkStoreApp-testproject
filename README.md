# DarkStoreApp-testproject
This is test task according to https://www.notion.so/darkstoreapp/Portfolio-Manager-API-Python-3f79ed6c559e4ef8ba6246108a76f3b0.
## How to run this project:
1. Copy this repo into your local file
2. Create virtual enviroment with this command: python -m venv .venv
3. Activate venv: source .venv/bin/activate
4. Copy repo-venv into local enviroment: pip install -r requirements.txt
5. Run the server: hypercorn main:app --reload
## How to use this project:
First of all you need to create an admin user, for that, please, /admin post methon in "Started Requirements" tag. You need this user to have access to "Admin Panel".
Then you should login with admin user parameters, login: admin, password: secret. After that you have access to all available methods.
You also can create your own user with Create User(3rd methon in "Started Requirements"). It will provide you access with all methods, not admin's ones.
## Bugs that i didn't manage to fix:
1.When you are creating new profile(post Create Profile method) please make shure that field user_id = your user id. You can see your user id while creating user,
or you can get JsonWebTocken in 'Generate Token' method and then go to https://jwt.io/ and paste your token.
2.Profile is not working with float values.  
3.Docker compose is not working.
