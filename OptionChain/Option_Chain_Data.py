import requests
import pandas as pd

access_token = "eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiIySENBWVAiLCJqdGkiOiI2NzI3YTllZmNhZjc2ZDUzNzg0YzRiNGIiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaWF0IjoxNzMwNjUyNjU1LCJpc3MiOiJ1ZGFwaS1nYXRld2F5LXNlcnZpY2UiLCJleHAiOjE3MzA2NzEyMDB9.WXOZxYlYQKPdFv9xbIHD8o_ja2y2pzMm56CpH1FkAlY"
def calculate_margin_for_contracts(data: pd.DataFrame) -> pd.DataFrame:
    # API endpoint for margin requirement
    margin_endpoint = "https://api.upstox.com/v2/charges/margin"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    margin_data = []


    for _, row in data.iterrows():
       
        instrument_key = row['instrument_key']
        quantity = row['lot_size']  
        transaction_type = "SELL"  
        product = "D"  


        payload = {
            "instruments": [
                {
                    "instrument_key": instrument_key,
                    "quantity": quantity,
                    "transaction_type": transaction_type,
                    "product": product,
                }
            ]
        }
        response = requests.post(margin_endpoint, headers=headers, json=payload)
        

        if response.status_code == 200:
            margin_info = response.json().get("data", {}).get("margins", [{}])[0]
            margin_required = margin_info.get("total_margin", None)  
            row['margin_required'] = margin_required
            row['premium_earned']= quantity*row['highest_bid/ask_price']
        else:
            print(f"Failed to fetch margin for instrument_key {instrument_key} - Status code: {response.status_code}")
            print(response.json())
            row['margin_required'] = None

        margin_data.append(row)
    
    margin_df = pd.DataFrame(margin_data)

    new_df = margin_df[['instrument_key', 'strike_price', 'side', 'highest_bid/ask_price', 'margin_required', 'premium_earned']]

    print("Margin and Premium earned")
    print(new_df)




def get_option_chain_data(instrument_name: str, expiry_date: str) -> pd.DataFrame:   
    instrument_key = f"NSE_INDEX|{instrument_name}"  
    #API-1(Option Contract)
    endpoint1 = "https://api.upstox.com/v2/option/contract"
    headers1 = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    
    params1 = {
        "instrument_key": instrument_key,
        "expiry_date": expiry_date
    }
    
    #API-2(Put/Call Option)
    endpoint2 = "https://api.upstox.com/v2/option/chain"
    headers2 = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    
    params2 = {
        "instrument_key": instrument_key,
        "expiry_date": expiry_date
    }



    response1 = requests.get(endpoint1, headers=headers1, params=params1)
    response2 = requests.get(endpoint2, headers=headers2, params=params2)


    if response1.status_code != 200:
        raise ValueError(f"Failed to fetch data: {response1.status_code}, {response1.text}")
    if response2.status_code != 200:
        raise ValueError(f"Failed to fetch data: {response2.status_code}, {response2.text}")
    
    data1 = response1.json().get("data", [])
    data2 = response2.json().get("data", [])

    if not data1:
        print("No data available for the specified parameters.")
        return pd.DataFrame()
    if not data2:
        print("No data available for the specified parameters.")
        return pd.DataFrame()
      
    df1 = pd.DataFrame(data1)
    df2 = pd.DataFrame(data2)
    results = []
    for _, row in df1.iterrows():
        expiry_date = row['expiry']
        strike_price = row['strike_price']
        ik = row['instrument_key']
        relevant_row = df2[(df2['expiry'] == expiry_date) & (df2['strike_price'] == strike_price)]
        lot = row['lot_size']
        if not relevant_row.empty:
            relevant_row = relevant_row.iloc[0] 

            if row['instrument_type'] == 'PE':  
                put_options = relevant_row['put_options']
                highest_bid_price = put_options['market_data']['bid_price']
                results.append({
                    'instrument_key': ik,
                    'lot_size': lot,
                    'expiry': expiry_date,
                    'strike_price': strike_price,
                    'highest_bid/ask_price': highest_bid_price,
                    'side': 'PE'
                })
            
            elif row['instrument_type'] == 'CE':  
                call_options = relevant_row['call_options']
                highest_ask_price = call_options['market_data']['ask_price']
                results.append({
                    'instrument_key': ik,
                    'lot_size': lot,
                    'expiry': expiry_date,
                    'strike_price': strike_price,
                    'highest_bid/ask_price': highest_ask_price,
                    'side': 'CE'
                })

    result_df = pd.DataFrame(results)
    
    new_df = result_df[['instrument_key', 'strike_price', 'side', 'highest_bid/ask_price']]
   
    print("highest BID/ASK")
    print(new_df)
    calculate_margin_for_contracts(result_df)
    
    
# Sample call 
get_option_chain_data("Nifty 50", "2027-12-30")
