Simple API FOR 2fa written in python with FastAPI

this app is actually a demo to present how to implement the registration + login + otp verification proces



For DEMO PORPUSE ALL DATA ARE IN SQL-LITE and the OTP is written in as auth_token of the /users/auth response! please don't take that as a good practice!


Commands to execute it

docker build -t myimage .  
docker run -d --name mycontainer -p 80:80 myimage

to execute tests (right after the previous commands)

docker exec mycontainer bash -c "pytest"