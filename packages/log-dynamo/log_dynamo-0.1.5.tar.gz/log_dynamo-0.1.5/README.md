## 注 
1. need create log_access/log_record dynamoDB table
## 表
### log_access
- pk: project#month
- sk(action):method#path
- other:
  - count
### log_record
- pk: project#day
- sk: created_time#func#user
- other:
  - func 
  - level
  - user
  - app
  - log