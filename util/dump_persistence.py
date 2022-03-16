import sys

from telegram.ext import PicklePersistence


filename = '../bot_persistence'

if len(sys.argv) == 2:
    filename = sys.argv[1]

persistence = PicklePersistence(filename=filename)

user_data = persistence.get_user_data()
print(user_data)
for user_key in user_data:
    user = user_data[user_key]
    if user:
        print(f"{user_key:<15} {user['effective_user']['username']:20} authorized: {str(user['authorized']):6} config: {user['config']}")
    else:
        print(f"{user_key:<15} -empty-")
