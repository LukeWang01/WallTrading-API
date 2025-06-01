<h1 align="center" style="margin: 0 auto 0 auto;"> 
   <img width="32" src="https://lookatwallstreet.notion.site/image/https%3A%2F%2Fprod-files-secure.s3.us-west-2.amazonaws.com%2F0472a71b-02f2-43f2-b650-2ae94ae1fb5b%2Fc0e93390-aca9-4f7a-8b36-8a66ec8d925f%2F%25E5%25BE%25AE%25E4%25BF%25A1%25E6%2588%25AA%25E5%259B%25BE_20240930173619.png?table=block&id=1296853c-146c-8096-bb90-d38181edfea5&spaceId=0472a71b-02f2-43f2-b650-2ae94ae1fb5b&width=600&userId=&cache=v2" alt="logo" >  
   WallTrading-API
</h1>
<h4 align="center" style="margin: 0 auto 0 auto;">
   
Auto sync all trading from the WallTrading Bot to your own account. Also provide the pre-build functions to market buy/sell, limit buy/sell, support MooMoo/Futu, IBKR, Schwab, Webull, Tiger

</h4>



## Instructions:

#### 0. Download the Python:
   - 3.10: https://www.python.org/downloads/release/python-31011/

<br>

#### 1. Clone the repository:

   ```bash
   git clone https://github.com/LukeWang01/WallTrading-API.git
   ```

or, just download the zip file from the repository.

<br>

#### 2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

<br>

#### 3. Set up the ID and Password in `env/_secrets.py`:
   - replace the API `ID` and `PASSWORD` with your own ID and Password.
   - replace any trading password as noted in the file. 

<br>

#### 4. Set up the `trading_settings.py`:
   - input your broker name as noted in the file.
   - change other settings as needed.

<br>

#### 5. Run any other required app as noted:
   - **MooMoo**: OpenD required, run the openD, set the port number to `11112`, and login to your MooMoo account. More info: [here](https://github.com/LukeWang01/WallTrading-Bot-MooMoo)
   - **SChwab**: Need to refresh the token weekly. More info: [here](https://github.com/angustar/schwab-generate-token)
   - **IBKR**: IB Gateway required. More info: [here](https://www.interactivebrokers.com/en/trading/ibgateway-stable.php?)
   - **Webull**: Need to get token, did, uuid manually, need to refresh the token weekly. More info: [here](https://github.com/LukeWang01/Program-Trading-Based-on-Webull/blob/main/docs/first_run_setup.md)

<br>


#### 6. Run the `run_client.py` to start the client:
   ```bash
   python run_client.py
   ```

<br>

#### 7.  Questions & Support via Discord:
- https://discord.gg/9uUpjyyqkZ


<br>

## More Info:
1. Subscribe the Bot and get start: [LookAtWallStreet](https://buy.stripe.com/3cscNB4zDbaU4mY8ww) on Scripe.

2. Visit the [LookAtWallStreet Home Page](https://lookatwallstreet.notion.site/11d6853c146c800992f2dcb48d18516d)



<br>

## Others:

1. Don't have MooMoo Account?
Feel free to use the link below to get a MooMoo account, 0 fees for most tradings. We both can get some free stocks. 💰
https://j.moomoo.com/011Pu5

2. Discord Server for program trading: https://discord.gg/9uUpjyyqkZ

3. Discord Server for tradingBOT, SOXL, TQQQ, BTC: https://www.patreon.com/LookAtWallStreet

   or, just add me on Discord. My Discord ID: squawkwallstreet

4. Other Trading Repos:
   
   Webull Bot Repo: https://github.com/LukeWang01/Program-Trading-Based-on-Webull
   
   MooMoo Bot Repo: https://github.com/LukeWang01/WallTrading-Bot-MooMoo

<br>

## Following up info, updated to 12/27/2024:

1. [2024年报：4月实盘至今，机器人策略，tqqq大幅跑赢大盘和基准；soxl跑平大盘，大幅跑赢基准
](https://mp.weixin.qq.com/s/4Vn2HsClTCQUYLJKiS5q_w)
![image](https://github.com/user-attachments/assets/69cab4ee-0eab-4908-8de3-5b1dc016ce10)
![image](https://github.com/user-attachments/assets/34b5ee1f-2dcd-4d70-9d8b-1793ba7b950f)
![image](https://github.com/user-attachments/assets/fc2faa15-d8ff-4d98-9be0-86b38a3be2f0)
![image](https://github.com/user-attachments/assets/09480e6d-288e-4439-b59c-afe866be6d76)
![image](https://github.com/user-attachments/assets/c868b0ea-499f-4014-bf03-d44117e15b80)


2. [机器人策略的秋收季](https://mp.weixin.qq.com/s?__biz=MzU2MDU4MjQ0NQ==&mid=2247487388&idx=1&sn=d235435f4acfd8a28913459f0f16dbf4&scene=21#wechat_redirect)

3. [机器人自动交易，低买高卖太逆天](https://mp.weixin.qq.com/s?__biz=MzU2MDU4MjQ0NQ==&mid=2247487356&idx=1&sn=827122f16e553cc4bbe006430383092a&scene=21#wechat_redirect)

4. [【Discord社区/机器人】答疑：为什么是tqqq，soxl，ibit？ 01](https://mp.weixin.qq.com/s?__biz=MzU2MDU4MjQ0NQ==&mid=2247487090&idx=1&sn=2d5ed32af45b0bd351bbf2575b1d375f&scene=21#wechat_redirect)
 
5. [【Discord社区/机器人】答疑：为什么是tqqq，soxl，ibit？ 02](https://mp.weixin.qq.com/s?__biz=MzU2MDU4MjQ0NQ==&mid=2247487100&idx=1&sn=5ead89f4ef5dcd94d412873d66ecb6cf&scene=21#wechat_redirect)

<br>

## Dev. Team:
- Luke
- Angus

Dev Version: 0.1.8

Developed by: (C) 2025 LookAtWallStreet
