# Slack-Lunch-Bot
선택장애가 있는 사람들을 위한 랜덤 점심 선택 및 점심 알리미 봇.

파이썬으로 제작한 Slack 점심 알리미 봇이다. 점심 메뉴를 데이터베이스에 등록해 놓으면, 지정시간마다 점심메뉴를 봇이 슬랙채널을 통해 알려준다.
## 0. Installation

슬랙 통신이 간혹 커넥션 에러를 발생하기 때문에 프로그램이 간혹 종료되거나, 기타 오류로 프로그램이 종료되는 경우
재시작을 자동으로 하기 위해 docker를 사용합니다.
0. docker를 설치한다. docker를 사용하지 않는 분들을 config파일을 수정하거나 docker파일은 지우고 직접 입력하면 된다.
1. docker-compose에 발급받은 slack-api-token을 추가한다.
2. `docker-compose up -d --build` 로 시작

## 1. 특징 및 사용방법


한 주마다 메뉴가 초기화되며 같은 음식을 먹을 일이 없게 한다. 


ex) 데이터베이스에 밥종류가 7가지(밥1, 밥2, 밥3, 밥4, 밥5, 밥6, 밥7)가 있다면 기본적으로 월요일 오전 9시에 메뉴가 7가지로 초기화가된다. 

그리고 메뉴를 자동으로 선택해주는 알림이 오게되면 그 메뉴는 삭제가된다.

'밥3'이 선택되어 알람이 온다면 밥3은 삭제되어 (밥1, 밥2, 밥4, 밥5, 밥6, 밥7) 이렇게 
남게되고 그 주에는 밥3은 다시는 선택되지 않게 된다.

이렇게 날마다 밥들이 선택되고 하나씩 줄어간다. 그렇기 때문에 한 주에 똑같은 메뉴를 먹을일이 없어진다.

그리고 매주 월요일 오전 9시에 새로(밥1, 밥2, 밥3, 밥4, 밥5, 밥6, 밥7)으로 초기화가 되고 다시 시작된다.

만약 밥종류가 3가지밖에 없다면 (밥1, 밥2, 밥3) 월, 화, 수 만에 밥3개를 다먹게 되면 월요일 오전 9시에 초기화되는거 처럼 자동으로 다시 초기화가 된다.

### 기본적인 프로그램 사용방법
1. 밥추천/추천/메뉴추천/메뉴 추천 ex) 밥추천
2. 추가/밥추가/메뉴추가 ex)밥추가 돈가스
3. 삭제/밥삭제/메뉴삭제 ex) 삭제 돈가스
4. 확인/메뉴기록/메뉴로그 ex) 확인 2018-11-07
5. 초기화/재세팅 ex) 초기화
6. 모든메뉴 ex) 모든메뉴
7. 알람설정 ex) 알람설정 110000
8. 기타설명
9. 채널변경 및 등록 ex) 등록

#### 1. 정상적인 채널의 알림을 위해 먼저 채널 등록을 한다
ex) 등록

#### 2. 알람설정은 매일 점심메뉴 알람이 오는 시간 설정으로써 HHMMDD 시간으로 항상 입력해준다. 
기본세팅은 110000이다. (오전 11시)
ex) 알람설정 153030 (3시30분30초)

#### 3. 메뉴로그는 날짜를 입력하게 되면 그날 어떤 음식이 자동으로 선택되었는지 알 수 있다.
항상 yyyy-mm-dd로 입력해준다.
ex) 확인 2018-11-07

## 2. Sqlite3 Table
```{.sql}
create table menu(
	name text not null primary key);

create table menu_log(
    id integer primary key autoincrement,
    name text not null,
    time timestamp DATE DEFAULT(datetime('now', 'localtime')));
```

기타 Slack Bot 생성 및 추가는 https://pangyeon.tistory.com/22?category=682581 확인할 수 있다.
