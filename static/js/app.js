// Your web app's Firebase configuration
var firebaseConfig = {
  apiKey: "AIzaSyBzsRUiJQgSxc-hlV-zJCCLP95fpFIpSpY",
  authDomain: "crop-monitoring-platform.firebaseapp.com",
  projectId: "crop-monitoring-platform",
  storageBucket: "crop-monitoring-platform.appspot.com",
  messagingSenderId: "654035213362",
  appId: "1:654035213362:web:50f1a9693fc06211bcb02b",
  measurementId: "G-3QQWW52Z18"
};
// Initialize Firebase
firebase.initializeApp(firebaseConfig);
// Initialize variables
const auth = firebase.auth()
const database = firebase.database()

// Set up our register function
function sign_up() {
  // Get all our input fields
  email = document.getElementById('email').value
  password = document.getElementById('password').value
  username = document.getElementById('username').value

  // Validate input fields
  if (validate_email(email) == false || validate_password(password) == false) {
    alert('Email or Password is Outta Line!!')
    return
    // Don't continue running the code
  }
  if (validate_field(username) == false) {
    alert('One or More Extra Fields is Outta Line!!')
    return
  }
 
  // Move on with Auth
  auth.createUserWithEmailAndPassword(email, password)
  .then(function() {
    // Declare user variable
    var user = auth.currentUser

    // Add this user to Firebase Database
    var database_ref = database.ref()

    // Create User data
    var user_data = {
      email : email,
      username : username,
      last_login : Date.now()
    }

    // Push to Firebase Database
    database_ref.child('users/' + user.uid).set(user_data)

    // DOne
    alert('User Created!!')
  })
  .catch(function(error) {
    // Firebase will use this to alert of its errors
    var error_code = error.code
    var error_message = error.message

    alert(error_message)
  })
}


// Set up our login function
function sign_in() {
  // Get all our input fields
  email = document.getElementById('email').value
  password = document.getElementById('password').value

  // Validate input fields
  if (validate_email(email) == false || validate_password(password) == false) {
    alert('Email or Password is Outta Line!!')
    return
    // Don't continue running the code
  }

  auth.signInWithEmailAndPassword(email, password)
  .then(function() {
    // Declare user variable
    var user = auth.currentUser

    // Add this user to Firebase Database
    var database_ref = database.ref()

    // Create User data
    var user_data = {
      last_login : Date.now()
    }

    // Push to Firebase Database
    database_ref.child('users/' + user.uid).update(user_data)

    // DOne
    // alert('User Logged In!!')
    console.log("login successful")
    window.location.replace("/map")
    console.log("result")

  })
  .catch(function(error) {
    // Firebase will use this to alert of its errors
    var error_code = error.code
    var error_message = error.message

    alert(error_message)
  })
}

// 


// Validate Functions
function validate_email(email) {
  expression = /^[^@]+@\w+(\.\w+)+\w$/
  if (expression.test(email) == true) {
    // Email is good
    return true
  } else {
    // Email is not good
    return false
  }
}

function validate_password(password) {
  // Firebase only accepts lengths greater than 6
  if (password < 6) {
    return false
  } else {
    return true
  }
}

function validate_field(field) {
  if (field == null) {
    return false
  }

  if (field.length <= 0) {
    return false
  } else {
    return true
  }
}

function google_login () {
  var provider = new firebase.auth.GoogleAuthProvider();
  firebase.auth()
    .signInWithPopup(provider)
    .then((result) => {
      /** @type {firebase.auth.OAuthCredential} */
      var credential = result.credential;

      // This gives you a Google Access Token. You can use it to access the Google API.
      var token = credential.accessToken;
      // The signed-in user info.
      var user = result.user;
      window.location.replace('/map')
      console.log("user===>", user.displayName)
    }).catch((error) => {
      var errorCode = error.code;
      var errorMessage = error.message;
      alert(errorMessage)
    });

}
function signout () {
  firebase.auth().signOut()
    .then(() => {
      window.location = "/"
    }
    )
    .catch(() => {

    }
    )
}