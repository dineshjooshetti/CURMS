// $("textarea[word-limit=true]").keydown(function() {
$(document).on('input', "textarea[word-limit=true]", function() {
  // Get individual limits
  thisMin = parseInt($(this).attr("min-words"));
  thisMax = parseInt($(this).attr("max-words"));
  // Create array of words, skipping the blanks
  var removedBlanks = [];
  removedBlanks = $(this).val().split(/\s+/).filter(Boolean);
  
  // Get word count
  var wordCount = removedBlanks.length;
  // Remove extra words from string if over word limit
  if (wordCount > thisMax) {
        // Trim string, use slice to get the first 'n' values
      var trimmed = removedBlanks.slice(0, thisMax ).join(" ");
      
      // Add space to ensure further typing attempts to add a new word (rather than adding to penultimate word)
      $(this).val(trimmed + " ");
	  wordCount=wordCount-1
      $(this).parent().parent().find(".feildCount").text(thisMax);
    }
    
 
  // Compare word count to limits and print message as appropriate
    if (wordCount <= thisMax) {
        $(this).parent().parent().find(".feildCount").text(wordCount);
    }
  if ( wordCount < thisMin) {
	//$(this).parent().parent().find(".err").text("Word count under " + thisMin);
    //$(this).parent().children(".writing_error").text("Word count under " + thisMin + ".");
  
  } 
  else if (wordCount >= thisMax) {
    //$(this).parent().parent().find(".feildCount").text(wordCount);
	// $(this).parent().parent().find(".error").text("Word count " + thisMax);
	$(this).next().find('.err').text("Word count " + thisMax)
    //$(this).parent().children(".writing_error").text("Word count over " + thisMax + ".");
  
  } else {
    
    // No issues, remove warning message
    $(this).next().find('.err').text("");

  }

});

$('textarea').each(function () {
  var removedBlanks = [];
  removedBlanks = $(this).val().split(/\s+/).filter(Boolean);

  // Get word count
  var wordCount = removedBlanks.length;
  console.log(wordCount)
  $(this).next().find(".feildCount").text(wordCount);


})
