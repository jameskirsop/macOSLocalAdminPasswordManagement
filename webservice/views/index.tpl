% include('header.tpl',title='Hello World')
<body>
    <h1>localadmin Password Decrypter</h1>
    % if error:
        <strong class="error">{{ error }}</strong>
    % end
    <p>Paste the contents of the 'Encrypted Local Administrator Password' fact from a devices' GoLive session from within Addigy to retrieve the <code>localadmin</code> account's password.</p>
    <form method="POST" action="">
        <!-- <input type="text" name="cipher-password" id=""> -->
        <textarea name="cipher-password" id="" cols="40" rows="10"></textarea>
        <button type="submit">Go!</button>
    </form>
</body>
</html>