window.fbAsyncInit = function() {
		FB.init({
			appId      : '1603413723087304',
			cookie     : true,
			xfbml      : true,
			version    : 'v2.12'
		});
		  
		FB.AppEvents.logPageView();
	};

	(function(d, s, id){
		var js, fjs = d.getElementsByTagName(s)[0];
		if (d.getElementById(id)) {return;}
		js = d.createElement(s); js.id = id;
		js.src = "https://connect.facebook.net/en_US/sdk.js";
		fjs.parentNode.insertBefore(js, fjs);
	}(document, 'script', 'facebook-jssdk'));

	function send_token_to_server(response) {
		if (response.status == 'connected') {
			$.ajax({
				type: 'POST',
				url: '/fbconnect?state={{STATE}}',
				processData: false,
				contentType: 'application/octet-stream; charset=utf-8',
				data: response['authResponse']['accessToken'],
				success: function(result) {
					if (result) {
						successful_login(result);
					} else if (response['status'] != 'connected') {
						console.log('There was an error, your connection status is: ' + response['status']);
					} else {
						$('#result').html('Failed to make a server side call. Check your configuration and console.');
					};
				}
			});
		} else {
			$('#result').html('Failed to make a server side call. Check your configuration and console.');
		};
	};

	function checkLoginState() {
		FB.getLoginStatus(function(response) {
		    send_token_to_server(response);
		});
	};