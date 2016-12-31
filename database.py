from firebase import firebase

firebase = firebase.FirebaseApplication('https://anvilappointments.firebaseio.com', None)
result = firebase.get('/users', None)
print result
