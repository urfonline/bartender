(function() {
	var app = new Vue({
		el: "#app-mount",
		data: {
			signedIn: false,
			loading: false,
			error: null,
			showName: "Unknown"
		},
		methods: {
			theButton: function() {
				// todo: clientside verification
				this.loading = true;

				fetch("/api/attend", { method: "POST" }).then((res) => {
					if (res.ok) {
						this.signedIn = true;
						this.loading = false;

						res.json().then((data) => {
							this.showName = data.show_name;
							console.log(data);
						});
					} else {
						res.json().then((data) => {
							this.error = data.error || "Failed to authenticate this computer.";
							this.loading = false;
						});
					}
				}).catch((err) => {
					this.error = err || true;
				});
			},
			reset: function() {
				this.error = null;
				this.loading = false;
				this.signedIn = false;

				// possible TODO: tell server we've reset after an error (or signed out?)
				new Notification("Register Your Show!", {
					body: "Remember to register your show!",
					silent: true
				});
			},
			checkStatus: function () {
				fetch("/api/status")
					.then((res) => res.json())
					.then((data) => {
						if (!data.attended) {
							this.reset();
						} else {
						    this.signedIn = true;
						    this.loading = false;

							if (data.show) {
								this.showName = data.show.name;
							}
                        }
					})
					.catch((err) => {
					    // this.error = err;
                        // Probably just ignore this one? Maybe flash a message
					});
			}
		}
	});

	setInterval(function() {
		app.checkStatus()
	}, 30000);

	window.devApp = app;

	Notification.requestPermission();
	app.checkStatus();
})();
