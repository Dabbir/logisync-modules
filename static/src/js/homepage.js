odoo.define('logisync-modules.homepage', function (require) {
    'use strict';
    
    var publicWidget = require('web.public.widget');
    
    publicWidget.registry.LogisyncHomepage = publicWidget.Widget.extend({
        selector: '.s_cover',
        events: {
            'click .btn-outline-light': '_scrollToFeatures',
        },
        
        start: function () {
            this._super.apply(this, arguments);
            this._initAnimations();
            return this;
        },
        
        _scrollToFeatures: function (ev) {
            ev.preventDefault();
            $('html, body').animate({
                scrollTop: $('#features').offset().top
            }, 1000);
        },
        
        _initAnimations: function () {
            // Animate cards on scroll
            var self = this;
            $(window).on('scroll', function () {
                self._animateOnScroll();
            });
            // Initial check
            this._animateOnScroll();
        },
        
        _animateOnScroll: function () {
            var windowHeight = $(window).height();
            var windowScrollTop = $(window).scrollTop();
            
            $('.card').each(function () {
                var elementTop = $(this).offset().top;
                
                if (elementTop < (windowScrollTop + windowHeight - 100)) {
                    $(this).addClass('animated fadeInUp');
                }
            });
            
            $('.timeline-step').each(function (index) {
                var elementTop = $(this).offset().top;
                
                if (elementTop < (windowScrollTop + windowHeight - 100)) {
                    var delay = index * 200;
                    $(this).delay(delay).addClass('animated fadeInLeft');
                }
            });
        }
    });
    
    return publicWidget.registry.LogisyncHomepage;
});