from firebase import firebase

if __name__ == '__main__':
    firebase = firebase.FirebaseApplication('https://anvilappointments.firebaseio.com', None)
    result = firebase.get('/users', None)
    print result
