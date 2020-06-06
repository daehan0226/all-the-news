## Front
1. user
    * Top words : 
        1. top 10 - 1 day, top 30 - 1 week, top 50 - 1 month 
        2. Top words 의 기사 링크 
        3. Top words 의 영영사전 
    * Flash game :
        1. 사용자가 저장한 단어 리스트
        2. 저장 시 힌트, 링크, 뜻, 예제 저장하기
        3. complete 섹션
        
2. admin
    * 크롤링 실행/정지 - 사이트별로 실행하기
    * 수집 결과 보기   - 수집 날자별로, 사이트별로 그래프로
    * 분석기
        1. 문서에서 단어 카운트해서 저장하기
        2. 저장한 단어 사전(한,영) 저장하기
    * es 정보

## Back - flask api

1. Crawler
    * bbc, cnn, npr, koreantimes, koreanherald  해외 또는 국내 영어 기사 사이트의 데이터 수집해서 es에 저장
    * es 에서 단어만 가져와서 단어 뜻 파싱해서 mysql 저장
    

2. Analyzer
    1. elasticsearch - index: top_words
        * 매일 그달의 10단어, 그 주의 top 단어, 그 달의 단어 분석 결과 저장하기
    
    2. mysql
        * users(uid,email,password)
        * words(wid, word, meaning)
        * user-word(uid,wid,hint)
        
3. Client logs - es
    time, ip, status, request
    
## Database

1. Elasticsearch
    * news
        1. mapping
       
    * logs
        1. mapping
     
    
2. Mysql
    * user
        1. 유저 정보
    
    * words
        1. 단어, 한 영 사전
        
    * user - words
        1. 유저가 저장한 단어, 힌트, 선택한 링크, 등 저장
        
    * top words
        1. 일,주,월 단위 단어
   