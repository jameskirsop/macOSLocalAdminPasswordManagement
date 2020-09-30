from bottle import route, run, template, post, request
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import binascii

@route('/')
def index():
    return template('index')

@post('/decrypt')
def decrypt():
    enc_data = binascii.unhexlify(request.forms.get('cipher-password'))
    with open("private.pem",'r') as f:
        local_key = RSA.import_key(f.read())
        cipher_rsa = PKCS1_OAEP.new(local_key)
        unenc_data = cipher_rsa.decrypt(enc_data)
        return template('password',{'decrypted_password':unenc_data})


run(host='localhost',port=8085,debug=True,reloader=True)