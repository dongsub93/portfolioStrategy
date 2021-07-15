# portfolioStrategy
This project aims to implement one's portfolio and to back-test the strategy on the market.

Authors of the project

  Kim, Hyeontae(htkim428@gmail.com)
  Lee, Dongsub(dongsub93@gmail.com)
  
----------------------------------
0. Pre-requisites

This project uses Python3.9(Compatibility with the other versions of Python is not checked yet) and requires following modules.

  - pandas
  - bs4
  - numpy
  - etc

Also there are some required libraries.

  - lib1
  - lib2
  - etc

Statistical data : http://ecos.bok.or.kr/flex/EasySearch.jsp?langGubun=K&topCode=060Y001

----------------------------------
1. Description on directories

There are three directories for now(2021.07.15.) as follow.

  - 00_data           : Containing relevant data
  - 01_main_scripts   : Containing main scripts to build a portfolio and the other auxiliary functions
  - 02_analysis_codes : Containing example codes and corresponding results

We left detailed description of them.

- 00_data
   - 0_marketList : Having the files in which list of securities in KOSPI are saved.
   - 1_pricesData : Having data of daily prices of securities and ETF. Also it has data of risk-free interest.
     - 0_riskFree : Having information about risk-free interest 
     - 1_ETF      : Having price information of some ETFs.
     - 2_stock    : Having price information of some stocks.
     
- 01_main_scripts           
   - analysis_functions.py : Definition of some functions relevant for analysis of portfolio history is written
   - aux_functions.py      : Helpful functions are defined.
   - crawler.py            : Functions for web-crawling are defined.
   - porfolio.py           : (class)'porfolio' is defined.
           
- 02_analysis_codes
   - example_fig.png         : Example output(figure) from 'porfolio_example.py'
   - example_history.csv     : Example output(backtest history in .csv format) from 'porfolio_example.py'
   - portfolio_example.ipynb : Example script for Jupyter
   - portfolio_example.py    : Example python script
           
        
           
----------------------------------
2. Usage
