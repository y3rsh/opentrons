docker build . -t remote_robot --build-arg ROBOT_URL=http://UNIQUE.ngrok.io

docker run -p 31950:31950 remote_robot