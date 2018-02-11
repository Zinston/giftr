function onSignIn(auth_result) {
	if (auth_result['code']) {

		$('#signin_button').attr('style', 'display: none');

		$.ajax({
			type: 'POST',
			url: '/gconnect?state={{STATE}}',
			processData: false,
			contentType: 'application/octet-stream; charset=utf-8',
			data: auth_result['code'],
			success: function(result) {
				if (result) {
					successful_login(result);
				} else if (auth_result['error']) {
					console.log('There was an error: ' + auth_result['error']);
				} else {
					$('#result').html('Failed to make a server side call. Check your configuration and console.');
				};
			}
		})
	};
}