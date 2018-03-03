//Based on the 2016 reddit april fools game: Grow!

//Newer chrome apps having manifest_version: 2 requires the tabs be opened as:
//
//chrome.browserAction.onClicked.addListener(function(activeTab)
//{
On browser load (the extension already runs on browser load):
//if user hasn't already given today:
//});

//to check if user has already given, ping their email to the server
chrome.identity.getProfileUserInfo(function(userInfo) {
    //userInfo.email, userInfo.id
    if (userInfo.email){ 
        //check whether user already gave today
        var GAMEPAGE = "http://give.appspot.com/give";
        chrome.tabs.create({ url: GAMEPAGE });
    } else {
        //user isn't logged in so, maybe open a page telling them to login?  
    }
});

//  Usage:

//  PERSISTENT Storage - Globally
//  Save data to storage across their browsers...

//chrome.storage.sync.set({ "yourBody": "myBody" }, function(){
    //  A data saved callback omg so fancy
//});

//chrome.storage.sync.get(/* String or Array */["yourBody"], function(items){
    //  items = [ { "yourBody": "myBody" } ]
//});

//  LOCAL Storage

// Save data to storage locally, in just this browser...

//chrome.storage.local.set({ "phasersTo": "awesome" }, function(){
    //  Data's been saved boys and girls, go on home
//});

//chrome.storage.local.get(/* String or Array */["phasersTo"], function(items){
    //  items = [ { "phasersTo": "awesome" } ]
//});