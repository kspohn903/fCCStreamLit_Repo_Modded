import streamlit as st, pandas as pd, base64, numpy as np #, seaborn as sns
import matplotlib.pyplot as plt, yfinance as yf
       st.title('S&P 500 App')
       st.markdown("""This app retrieves the list of the **S&P 500** (from Wikipedia) and its corresponding **stock closing price** (year-to-date)!
                    * **Python libraries:** base64, pandas, streamlit, numpy, matplotlib, seaborn
                    * **Data source:** [Wikipedia](https://en.wikipedia.org/wiki/List_of_S%26P_500_companies).""")
       st.sidebar.header('User Input Features') # Web scraping of S&P 500 data
 
       @st.cache
       def load_data():
           url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
           html = pd.read_html(url, header=0)
           # print(f"html: {html}\n")
           df = html[0]
           # print(f"df: {df}\n")
           return df

                
       df = load_data()
       # print(f"df:{df}\n")
       sector = df.groupby('GICS Sector')
       # print(f"sector: {sector}\n")
       # # Sidebar-Sector selection
       sorted_sector_unique = sorted(df['GICS Sector'].unique() )
       selected_sector = st.sidebar.multiselect('Sector',sorted_sector_unique, sorted_sector_unique)
       # print(f"sorted_sector_unique: {sorted_sector_unique}\n")

       # Filtering data
       df_selected_sector = df[(df['GICS Sector'].isin(selected_sector)) ]
       # print(f"df_selected_sector: {df_selected_sector}\n")

       st.header('Display Companies in Selected Sector')
       st.write("Data Dimension: {} rows and {} columns.\n".format(str(df_selected_sector.shape[0]),
                                                                   str(df_selected_sector.shape[1]) ))
       st.dataframe(df_selected_sector)

       # Download S&P500 data # https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806
       def filedownload(df):
           csv = df.to_csv(index=False)
           b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
           href = '<a href="data:file/csv;base64,{}" download="SP500.csv">Download CSV File</a>'.format(b64)
           # print(f"href: {href}\n")
           return href

       st.markdown(filedownload(df_selected_sector), unsafe_allow_html=True) # https://pypi.org/project/yfinance/
       data = yf.download(tickers = list(df_selected_sector[:10].Symbol),
                          period = "10yr", # 1d,5d,1mo,3mo,6mo,1yr,2yr,5yr,10yr,ytd,max; default is 10yr 
                          interval = "3mo", # 1m, 2m,5m,15m,30m,60m,90m,1h,1d,5d,5d,1wk,1mo,3mo,
                          group_by = 'ticker', 
                          auto_adjust = True, # adjust all OHLC automatically
                          prepost = True, # Download pre/post market hours data
                          threads = True, # Threads for mass download of data? True/False/Integer
                          proxy = None # Proxy URL Schemas used when downloading; usually for ML Proxies...; Default is None
                         )

       # Plot Closing Price of Query Symbol 
       def price_plot(symbol):
           df = pd.DataFrame(data[symbol].Close)
           df['Date'] = df.index
           # print(f"df: {df}\ndf['Date']: {df['Date']}\n")
           plt.fill_between(df.Date, df.Close, color='skyblue', alpha=0.3) 
           plt.plot(df.Date, df.Close, color='skyblue', alpha=0.8) # alpha=conf.level ?
           plt.xticks(rotation=90)
           plt.title(symbol, fontweight='bold')
           plt.xlabel('Date-Time (YYYY-MM-DD)',fontweight='bold')
           plt.ylabel('Closing Price', fontweight='bold')
           return st.pyplot()

              
       noCompaniesMax = 5
       num_company = st.sidebar.slider('Number of Companies',1, noCompaniesMax)

       if st.button('Show Plots'):
          st.header('Stock Closing Price')
          for el in list(df_selected_sector.Symbol)[:num_company]:
              price_plot(el)
