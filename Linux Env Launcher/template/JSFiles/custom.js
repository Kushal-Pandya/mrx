/*

	Goshow Web Launcher 

	Using Flask Server (running on localhost:5003) for GoShow App
	Using Jquery with AJAX to get JSON arrays from server

	HTML: indexT.html
	CSS: styleT.css along with Bootstrap

	Files: server.py and src.py under goshow folder

*/



//Function to start jquery and populate show drop down menu
$( document ).ready(function() {
	initApp()

	var width = 1250
	var height = 940 

	// Default window size
	window.resizeTo(width, height)

	//Initially constructing shotsMenu 
	$("#shotsMenu").select2()
	$('#shotsMenu').prop('disabled', true)
})

//Need global vars
var tasksData
var goshowHistory

function initApp() {
// Events
// Loading animation AJAX start/stop events - http://stackoverflow.com/questions/1964839/how-can-i-create-a-please-wait-loading-animation-using-jquery

	$(document).on({
		ajaxStart: function () { $('body').addClass('loading') },
		ajaxStop: function () { $('body').removeClass('loading') }
	})

	//Event Handlers to dynamically change things in drop-down menu
	$('#shows').on('click', '.show', showChanged)
	$('#apps').on('click', '.app', getVersions)
	$('#apps').on('click', '.app', getLicenses)
	$('#versions').on('click', '.version', setVersion)
	$('#vrays').on('click', '.vray', showVrayVersion)
	$('#thisLaunch').on('click', launchApp)

	//Event handling for auto goshow tasks
	$('#taskList').on('click', '.subtask', autoTasks) 

	//Handler for shotsMenu
	$('#shotsMenu').on('change', testShotChanged)

	//Event Handler for History Drop Down
	$('#history').on('click', '.hist', historyChanged)

	//Initially hiding/disabling buttons 
	$('#vrayList').hide()
	$('#thisShot').prop('disabled', true)
	$('#thisApp').prop('disabled', true)
	$('#thisVers').prop('disabled', true)
	$('#thisLaunch').prop('disabled', true)
	$('#loggerCheck').prop('disabled', true)


	initTasks()
	initShows()
	showHistory()
}

function initTasks() {
	$.get("http://localhost:5003/getTasks")
	.done(function (data) {
		user = "Tasks for: " + data.user
		delete data.user
		$('#taskUser').text(user) 
		tasksData = data
		showTasks(data)
	})
}


function showTasks(tasks) {
	var projects = Object.keys(tasks)
	for (var i=0; i < projects.length; i++) {
		$('#taskList').append(			
			$('<br>' + '<a/>' + '<br>').addClass('task').attr('href', '#').text(projects[i])
		)	

		subtask = tasks[projects[i]]
		for (var j=0; j < subtask.length; j++) {
			$('#taskList').append(
				$('<a/>' + '<br>').addClass('subtask').attr('href', '#').text(subtask[j])				
			)
		}
	}
}

function autoTasks() {
	var shot = $(this).text()

	$.get("http://localhost:5003/getTasksNames")
	.done(function (data) {

		var projects = Object.keys(tasksData)

		//Taking out 'Mr .X' out of the projects list as it
		// is not used for GoShow
		if (isInArray('Mr. X', projects) == true) {
			var index = projects.indexOf('Mr. X')
			if (index > -1) {
    			projects.splice(index, 1)
			}
		}

		for (var i=0; i < projects.length; i++) {

			subtask = tasksData[projects[i]]
			if (isInArray(shot, subtask) == true) {

				var show = projects[i]
				var shotArr = shot.split(':')
				shot = shotArr[0]

				//Checking other name object to translate show name
				show = data[show]

				$('#currentShow').text(show)
				$('#thisShot').prop('disabled', false)
				keepShotsMenu(show, shot)
				shotChanged(shot)
			}
		}
	})
}

function isInArray(value, array) {
	return array.indexOf(value) > -1;
}

//Function similar to updateShots, need different for autoTasks
function keepShotsMenu(show, shot) {
	var currentShow = show
	$.get('http://localhost:5003/getShows', {show: currentShow})
	.done(function (data) {

		//Since you cant overwrite the text, constructing new shotsMenu
		$('#shotsMenu').prop('disabled', false)
		$("#shotsMenu").empty()
		$("#shotsMenu").append($('<option>', {value: shot, text: shot}))
		$("#shotsMenu").select2({
			data: data.shots
		})
	})
}

function showHistory() {
	$.get("http://localhost:5003/getHistory")
	.done(function (data) {
		goshowHistory = data.history
		var histMenu = []

		for (var i=0; i<Object.size(goshowHistory); i++) {
			var string = (i+1 + '. Show: ' + goshowHistory[i].show + ' Shot: ' +
				goshowHistory[i].shot)
			histMenu.push(string)
		}
		$('#history li').remove()
		$.each(histMenu, function (i) {
			$('#history').append(
				$('<li/>').append(
					$('<a/>').addClass('hist').attr('href', '#').text(histMenu[i])
				)
			)
		})
	})
}

function historyChanged() {
	var currentHist = $(this).text()
	$('#currentHist').text(currentHist)

	var index = currentHist.split('.')[0]
	for (var i=0; i<Object.size(goshowHistory); i++) {
		if (index == goshowHistory[i].index) {
			var show = goshowHistory[i].show
			var shot = goshowHistory[i].shot
		}
	}
	$('#currentShow').text(show)
	$('#thisShot').prop('disabled', false)
	keepShotsMenu(show, shot)
	shotChanged(shot)
}

// Returns the size of the object
// Source: http://stackoverflow.com/questions/5223/length-of-a-javascript-object-that-is-associative-array
Object.size = function(obj) {
    var size = 0, key;
    for (key in obj) {
        if (obj.hasOwnProperty(key)) size++;
    }
    return size;
}

function initShows() {
	$.get("http://localhost:5003/init")
	.done(function (data) {
		updateShows(data)
	})
	.fail(function (data) {
		echoMsg('Unable to fetch show information: ' + '\nFailed ' + JSON.stringify(data), 'show-fail', 'alert-danger')
	})
}

function updateShows(show_data) {
	var shows = show_data.shows
	var set_show = 'Please select a show'
	
	//creating HTML attributes for each show while adding them
	$('#shows li').remove()
	$.each(shows, function (i) {
		$('#shows').append(
			$('<li/>').append(
				$('<a/>').addClass('show').attr('href', '#').text(shows[i])
			)
		)
	})
	$('#currentShow').text(set_show) 
}

function showChanged() {

	var currentShow = $(this).text()
	$('#currentShow').text(currentShow)

	$.get('http://localhost:5003/getShows', {show: currentShow})
	.done(function (data) {
		updateShots(data)
	})
	.fail(function (data) {
		echoMsg('Unable to fetch shot information: ' + '\nFailed ' + JSON.stringify(data), 'shot-fail', 'alert-danger')
	})
}

function updateShots(theShots) {
	$('#shotsMenu').prop('disabled', false)
	$("#shotsMenu").empty()

	$("#shotsMenu").append($('<option>', {value: 'Please', text: 'Please select a shot/asset'}))
	$("#shotsMenu").select2({
		placeholder: "Please select a shot",
		data: theShots.shots
	})
}

function testShotChanged() {
	// Using select2 to remove initial option
	$("#shotsMenu option[value='Please']").remove()
	currentShot = $("#shotsMenu").select2('val')

	shotChanged(currentShot)
}

//Function gets Apps using AJAX
function shotChanged(currentShot) {
	$.get('http://localhost:5003/getApps', {shot : currentShot})
	.done(function (data) {
		selectApp(data)
		initNotes()
		initThumbnail()
	})
	.fail(function (data) {
		echoMsg('Unable to fetch shot details information: ' + '\nFailed ' + JSON.stringify(data), 'shot-info-fail', 'alert-danger')
	})
}

function selectApp(data) {
	var apps = data.apps
	var set_app = 'Please select Application'
	$('#thisApp').prop('disabled', false)
	$('#apps li').remove()
	$.each(apps, function (i) {
		$('#apps').append(
			$('<li/>').append(
				$('<a/>').addClass('app').attr('href', '#').text(apps[i])
			)
		)
	})
	$('#currentApp').text(set_app)
}

function initNotes() {
	var currentShot = $("#shotsMenu").select2('val')
	var currentShow = $('#currentShow').text()

	$.get('http://localhost:5003/getNotes', {show: currentShow, shot: currentShot})
	.done(function (data) {
		showNotes(data.notes)
	})
	.fail(function (data) {
		echoMsg('Unable to fetch shot details information: ' + '\nFailed ' + JSON.stringify(data), 'shot-info-fail', 'alert-danger')
	})
}

//Fetch shotID from shotgun to get thumbnail
function initThumbnail() {
	var currentShot = $("#shotsMenu").select2('val')
	var currentShow = $('#currentShow').text()

	$.get('http://localhost:5003/getShotImage', {show: currentShow, shot: currentShot})
	.done(function (data) {
		showNewThumbnail(data.id)
	})
	.fail(function (data) {
		echoMsg('Unable to fetch shot details information: ' + '\nFailed ' + JSON.stringify(data), 'shot-info-fail', 'alert-danger')
	})
}

function showNewThumbnail(shotID) {
//Taken from: http://stackoverflow.com/questions/14651348/checking-if-image-does-exists-using-javascript
	// The "callback" argument is called with either true or false
	// depending on whether the image at "url" exists or not.
	function imageExists(url, callback) {
		var img = new Image()
	  	img.onload = function() {callback(true)}
	  	img.onerror = function() {callback(false)}
	  	img.src = url
	}

	var imageUrl = 'http://shotgun.mrxfx.com/thumbnail/full/Shot/' + shotID
	imageExists(imageUrl, function(exists) {
	  	console.log('RESULT: url=' + imageUrl + ', exists=' + exists)
	  	if (exists == true) {
	  		$("#image").attr('src', imageUrl)
	  	}
	})
}

function showNotes(data) {

	dataLen = data.length
	content = []
	timeUpdated = []
	repliesArr = []
	notes = []
	addressTo = []
	user = []

	printNotes = ""
	$('#notes').text("")

	//Parsing and formatting notes
	for (var i=0; i<dataLen; i++) {
		content[i] = JSON.stringify(data[i].content).trim()
		timeUpdated[i] = JSON.stringify(data[i].updated_at).trim()
		addressTo[i] = JSON.stringify(data[i].addressings_to[0].name)
		user[i] = JSON.stringify(data[i].user.name)

		var replyLen = data[i].replies.length
		for (var j=0; j<replyLen; j++) {
			repliesArr[j] = (data[i].replies[j].name).trim()
			repliesArr[j] = repliesArr[j].replace(/(\r\n|\n|\r)/gm, " ")
		}

		content[i] = content[i].replace(/(\r\n|\n|\\n|\r)/gm, " ")
		content[i] = content[i].replace(/"/g, '')
		timeUpdated[i] = timeUpdated[i].replace(/"/g, '')
		addressTo[i] = addressTo[i].replace(/"/g, '')
		user[i] = user[i].replace(/"/g, '')

		//Concatenating notes together
		notes[i] = "Time Updated: " + timeUpdated[i] + "\tTo: " 
			+ addressTo[i] + "\tFrom: " + user[i] + "\n\t" 
			+ content[i] + "\n\n\t\t"

		//Concatenating replies to each note
		for (j=0; j<replyLen; j++) {
			notes[i] = notes[i] + 'Reply: ' + repliesArr[j] + '\n\t\t'
		}
		notes[i] = notes[i] + "\n\n" 
	}

	//Concatenating to large string then Printing Notes to textarea
	for (var k=0; k<notes.length; k++) {
		printNotes = printNotes + notes[k]
	}
	$('#notes').text(printNotes)
}

function getLicenses() {

	var currentApp = $(this).text()
	var currentShow = $('#currentShow').text()
	var currentShot = $("#shotsMenu").select2('val')
	
	$('#currentApp').text(currentApp)
	$('#vrayList').hide("slow");

	$.get('http://localhost:5003/getLicenses', {app: currentApp})
	.done(function (data) {

		if (currentApp == 'Maya') {
			showVray(currentShow, currentShot)
		}
		showLicenses(data)
	})
	.fail(function (data) {
		echoMsg('Unable to fetch shot details information: ' + '\nFailed ' + JSON.stringify(data), 'shot-info-fail', 'alert-danger')
	})

}

function showLicenses(lics) {

	//Cleaning JSON string of lics to be human-readable
	var str = JSON.stringify(lics.licenses, null, 2)
	str = str.replace(/[\])}[{(]/g, '') 
	str = str.replace(/"/g, '')
	str = str.replace(/,/g, '')
	str = str.replace(/\\n/g, " ")
	str = str.replace(/\\t/g, " ")
	
	if (str !== 'temp') {
		$('#licList').text(str)
	}

	var currentApp = $('#currentApp').text()
	if (currentApp == 'Vray') {
		$('#licList').text('')
	}
}

function getVersions() {
	var currentApp = $(this).text()
	$('#currentApp').text(currentApp)
	$('#thisLaunch').prop('disabled', false)
	$('#loggerCheck').prop('disabled', false)

	var currentShow = $('#currentShow').text()
	var currentShot = $("#shotsMenu").select2('val')

	//Hides vray dropdown menu if another app is chosen
	$('#vrayList').hide("slow");

	$.get('http://localhost:5003/getVersions', {app: currentApp, 
		show:currentShow, shot: currentShot})
	.done(function (data) {
		if (currentApp == 'Maya') {
			showVray(currentShow, currentShot)
		}
		updateVersions(data)
	})
	.fail(function (data) {
		echoMsg('Unable to fetch shot details information: ' + '\nFailed ' + JSON.stringify(data), 'shot-info-fail', 'alert-danger')
	})
}

function updateVersions(data) {
	var versions = data.versions
	var set_version = versions[0]
	$('#thisVers').prop('disabled', false)

	$('#versions li').remove()
	$.each(versions, function (i) {
		$('#versions').append(
			$('<li/>').append(
				$('<a/>').addClass('version').attr('href', '#').text(versions[i])
			)
		)
	})
	$('#currentVersion').text(set_version)
}

function showVray(currentShow, currentShot) {
	$('#vrayList').show("medium")

	$.get('http://localhost:5003/getVrayVersions', {show: currentShow, 
		shot: currentShot})
	.done(function (data) {
		updateVrayVersions(data)
	})
	.fail(function (data) {
		echoMsg('Unable to fetch shot details information: ' + '\nFailed ' + JSON.stringify(data), 'shot-info-fail', 'alert-danger')
	})

}

function updateVrayVersions(data) {
	var vrays = data.vrayVersions
	var set_version = vrays[0]
	$('#vrays li').remove()

	$.each(vrays, function (i) {
		$('#vrays').append(
			$('<li/>').append(
				$('<a/>').addClass('vray').attr('href', '#').text(vrays[i])
			)
		)
	})
	$('#currentVray').text(set_version)
}

function showVrayVersion() {
	var currentVray = $(this).text()
	$('#currentVray').text(currentVray)
}


//Checking if launch Application button was clicked
function setVersion() {
	var currentVersion = $(this).text()
	$('#currentVersion').text(currentVersion)
	$('#thisLaunch').prop('disabled', false)
}

function launchApp() {

	//Retrieving info from drop down menus
	var currentApp = $('#currentApp').text()
	var currentShow = $('#currentShow').text()
	var currentShot = $("#shotsMenu").select2('val')
	var currentVray = $('#currentVray').text()
	var currentVersion = $('#currentVersion').text()
	var isLog = $('#loggerCheck').prop('checked') 	

	//Makes sure keyword 'default' isnt in version and vray version
	str = "Default"
	if (currentVersion.substring(0,7) == str) {
		currentVersion = currentVersion.replace('Default Version: ', '')
	}
	if (currentVray.substring(0,7) == str) {
		currentVray = currentVray.replace('Default Vray: ', '')
	}

	//Checking if "Please" is in any of the original dropdown menu names
	//if it is, then user needs to input all info
	//else launch app
	str = ("Please")
	if (currentVersion.substring(0,6) == str || 
		currentApp.substring(0,6) == str || 
		currentShot.substring(0,6) == str|| 
		currentShow.substring(0,6) == str) {
		$('#myModal').modal('show') 
		$('#modalHeader').text('Error')
		$('#modalText').text('Please fill out all the information')
	}
	else {

			$('#myModal').modal('show')
			$('#modalHeader').text('Launching ' + currentApp + ' Please Wait...') 
			$('#modalText').text('version: ' + currentVersion 
				+ ' with show: ' + currentShow + ' and shot: ' 
				+ currentShot)

		$.get('http://localhost:5003/launchApp', {app: currentApp, 
			show: currentShow, shot: currentShot, 
			version: currentVersion, vray: currentVray, logger: isLog})
		.done(function (data) {
			showHistory()
		})
	}
}
