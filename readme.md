# HackJMI-2 ML Security

Making a robust face recognition security system that doesn't lets the user with fake images i.e. holding up someone else's photo in front of camera to gain access.

This is the link to watch our team lead test the entire pipeline

[Demonstration video](https://drive.google.com/file/d/1zMBbUbwI77aQNUU-Pyer-GMChL2kwVj_/view)
<br>

--------------

<br>

![cheems gamg](website_v5/static/images/favicon.png)
## Team Cheems Gamg
1. Mohammad Abbas Ansari (Team Lead)
2. Mohammad Kashif (ML member)
3. MD Haider Zama (ML member)
4. MD Rashid Hussain (Web Dev member)

<br>

----------------

## [Our Spoof Detector Model](https://drive.google.com/file/d/105zAfafmc2tDHCJwGp9E5KllNCrCSpeE/view?usp=sharing) 

Click the above link to follow, If it does not work, use this https://drive.google.com/file/d/105zAfafmc2tDHCJwGp9E5KllNCrCSpeE/view?usp=sharing

(The model side combined with other files in the repository exceeds 500 MiB and so cannot be pushed to github)
<br>

--------------

## How to run ???
1. Clone this repository by running this command in your terminal/powershell/command prompt
    ```
    git clone https://github.com/hashes-jmi/HackJMI2-CheemsGamg.git
    ```
2. Install the below mentioned dependencies using conda or pip

3. Download the model from the given google drive [link](https://drive.google.com/file/d/105zAfafmc2tDHCJwGp9E5KllNCrCSpeE/view?usp=sharing) in the model directory. At last your model's path should be like this 
    ```
    /website_v5/model/clf.h5
    ``` 
4. change directory to website_v5 using the command
    ```
    cd website_v5
    ``` 
    and run the app.py file using 
    ```
    python app.py (if you are on windows)
    ``` 
     or 
    ```
    python3 app.py (if you are on linux or mac)
    ```
5. Open the link (output in the terminal) in your favourite browser and enjoy 😎😎😎

<br>

-------------
<br>

## To run this project locally on your system, you will need to install the following dependencies
```
1.  Python (v3.8.10)
2.  Flask (v2.0.2)
3.  Flask-SQLAlchemy (v2.5.1)
4.  tensorflow (v2.6.0)
5.  keras (v2.6.0)
6.  opencv (v4.5.3)
7.  torch (v1.9.1)                
8.  torchvision (v0.10.1
9.  keras-vggface (v0.6)
10. facenet-pytorch (v2.5.2)
11. scipy (v1.4.1)
12. numpy (v1.19.5)
13. matplotlib (v3.4.3)
15. pillow (>= v7.0.0)
```