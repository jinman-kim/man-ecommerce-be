# app/sql/user_queries.py

# 사용자 관련 쿼리들

GET_USER_BY_USERNAME = """
SELECT id, username, hashed_password
FROM users
WHERE username = $1
"""

CREATE_USER = """
INSERT INTO users (username, hashed_password)
VALUES ($1, $2)
"""

DELETE_USER = """
DELETE FROM users
WHERE id = $1
"""

# 필요한 추가 쿼리들을 여기에 추가하세요.
