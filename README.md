## Crontab

1. Crawler
    * bbc, cnn, npr, koreantimes, koreanherald   등 해외 또는 국내 영어 기사 사이트의 데이터 수집해서 es에 저장
    * es 에서 단어만 가져와서 단어 뜻 파싱해서 mysql 저장

2. Analyzer
    1. elasticsearch - index: top_words
        * 매일 그달의 10단어, 그 주의 top 단어, 그 달의 단어 분석 결과 저장하기
    
    2. mysql
        * users(uid,email,password)
        * words(wid, word, meaning)
        * user-word(uid,wid,hint)

## Front
* top 기사들 사이트별 보여주기
* 그날, 그 주 반복된 단어 리스트
* 단어 클릭 시 단어 영영사전 가져오기
* 단어 flashcard 게임 위에 단어 밑에 답보기 버튼 누르면 답 보여줌
* 객관식 문제 영영사전 뜻 풀이로 단어 맞추기