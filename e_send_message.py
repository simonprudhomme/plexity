import plivo

def text_people(message):
    client = plivo.RestClient(auth_id='MAMJNKYZQ2NMY3ZMI4ND', auth_token='ZWUyZDkyNzQ1ZDQ2MjFhM2UzZDhhMjgyOTkzM2Jl')
    message_created = client.messages.create(src='+1-579-791-6566',dst='+1-438-921-6292',text=message)
    return message_created