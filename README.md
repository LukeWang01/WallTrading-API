<h1 align="center" style="margin: 0 auto 0 auto;"> 
   <img width="32" src="https://lookatwallstreet.notion.site/image/https%3A%2F%2Fprod-files-secure.s3.us-west-2.amazonaws.com%2F0472a71b-02f2-43f2-b650-2ae94ae1fb5b%2Fc0e93390-aca9-4f7a-8b36-8a66ec8d925f%2F%25E5%25BE%25AE%25E4%25BF%25A1%25E6%2588%25AA%25E5%259B%25BE_20240930173619.png?table=block&id=1296853c-146c-8096-bb90-d38181edfea5&spaceId=0472a71b-02f2-43f2-b650-2ae94ae1fb5b&width=600&userId=&cache=v2" alt="logo" >  
   WallTrading-API
</h1>
<h4 align="center" style="margin: 0 auto 0 auto;">
Developed by: (C) 2024 LookAtWallStreet

<br>

### Instructions:

0. Download the Python:
   - 3.10: https://www.python.org/downloads/release/python-31011/

<br>

1. Clone the repository:

   ```bash
   git clone https://github.com/LukeWang01/WallTrading-API.git
   ```

or, just download the zip file from the repository.

<br>

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

<br>

3. Set up the ID and Password in `env/_secrets.py`:
   - replace the API `ID` and `PASSWORD` with your own ID and Password.
   - replace any trading password as noted in the file. 

<br>

4. Set up the `trading_settings.py`:
   - input your broker name as noted in the file.
   - change other settings as needed.

<br>

5. Run any other required app as noted:
   - MooMoo: run the openD, set the port number to `11112`, and login to your MooMoo account. More info: [here](https://github.com/LukeWang01/WallTrading-Bot-MooMoo)
   - SChwab: TBA
   - IBKR: TBA
   - Webull: TBA

<br>

6. Run the `run_client.py` to start the client:
   ```bash
   python run_client.py
   ```

<br>


### API Work Flow:
![image](https://github.com/user-attachments/assets/c9e14ec1-c2b2-47e7-ab2e-36e0d4bc3ebb)

<br>

Dev. Team:
- Luke
- Angus

Dev Version: 0.0.1

<br>

### Other Info:
Get more info from [LookAtWallStreet](https://www.patreon.com/LookAtWallStreet) on Patreon.

##### Don't have MooMoo Account?
Feel free to use the link below to get a MooMoo account, 0 fees for most tradings. We both can get some free stocks. 💰
https://j.moomoo.com/011Pu5

##### Discord Server for program trading:
https://discord.gg/9uUpjyyqkZ

##### Discord Server for tradingBOT, SOXL, TQQQ, BTC:
https://www.patreon.com/LookAtWallStreet

or, just add me on Discord. My Discord ID: squawkwallstreet

##### Other Trading Repos:
Webull Bot Repo: https://github.com/LukeWang01/Program-Trading-Based-on-Webull

MooMoo Bot Repo: https://github.com/LukeWang01/WallTrading-Bot-MooMoo

