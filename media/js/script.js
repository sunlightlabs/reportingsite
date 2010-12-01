$().ready( function() {
	
	var slideWidth = 575;
	var carouselUserIntervention = false;
	$('.carousel ul').css({'width': $('.carousel li').length * slideWidth});
	$('.carousel ul').prepend($('.carousel li:last'));
	
	var carouselNext = function() {
		$('.carousel li:first').animate(
			{width: 0},
			{queue: false, duration: 300, complete: function() {
				$('.carousel ul').append($(this).css({'width': slideWidth}));
			}}
		);
	};
	
	var carouselPrevious = function() {
		$('.carousel ul').prepend($('.carousel li:last').css({'width': 0}));
		$('.carousel li:first').animate(
			{width: slideWidth},
			{queue: false, duration: 300}
		);
	};
	
	var carouselAutoAdvance = function() {
		if (carouselUserIntervention) return;
		carouselNext();
		setTimeout(carouselAutoAdvance, 10000);
	}

	$('a.carousel-next').click(function(ev) {
		carouselNext();
		carouselUserIntervention = true;
		ev.preventDefault();
	});
	
	$('a.carousel-previous').click(function(ev) {
		carouselPrevious();
		carouselUserIntervention = true;
		ev.preventDefault();
	});
	
	setTimeout(carouselAutoAdvance, 10000);
	
});

