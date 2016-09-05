(function(){
  "use strict";
  /**
    This module aims to add the datetooltips described in #145
    for every `.datetooltip` that has a `> input`.
  */
  return define(['jquery', 'bootstrap'], function($){
    var computeText = function($input){
      var x = parseInt($input.val(), 10);
      if(x < 2000){
        return 'AD '+(2000-x);
      }else if(x > 2000){
        return (x-2000)+' BC';
      }else if(x === 2000){
        return 'AD 1';
      }
    };
    $('.datetooltip').each(function(){
      var $datetooltip = $(this);
      $datetooltip.attr('data-toggle', 'tooltip')
                  .attr("data-placement", "bottom")
                  .attr("data-container", "body");
      $datetooltip.find('input').each(function(){
        var $input = $(this);
        $input.change(function(){
          $datetooltip.tooltip('hide')
                      .attr('data-original-title', computeText($input))
                      .tooltip('fixTitle')
                      .tooltip('show');
        });
        $datetooltip.attr('title', computeText($input)).tooltip();
      });
    });
  });
}());
