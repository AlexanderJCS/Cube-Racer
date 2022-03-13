# Cube-Racer
A Rubik's cube racer

How to run a server (hopefully I'll make this easier in the future, but for right now):
1. Install Node.js. This is need to generate a scramble.
2. Have python installed.
3. Install pyTwistyScrambler via pip: https://github.com/euphwes/pyTwistyScrambler
4. Set the IP constant to your local IP. Can be found under "IPv4 Address" in ipconfig (Windows)
5. If people are connecting from outside your LAN, you must port forward (default port to port forward is 1234)

How to connect to a server:
1. Download and extract client_exe.zip
2. Run client_console.exe (NOT client.exe)
3. Input the server's local IP if you are connecting from LAN, otherwise put their public IP (must be port forwarding)
4. Input the port (default is 1234)
5. Provide your username. Times will be inaccurate if the username is the same as another user's.

How to race others:
1. Scramble your cube using the provided scramble on the top of the screen.
2. Press any key to start inspection.
3. Press any key again to start the timer.
4. When finished solving your cube, press any key to end the timer.
5. When a new scramble is shown, press any key to start inspection again.
