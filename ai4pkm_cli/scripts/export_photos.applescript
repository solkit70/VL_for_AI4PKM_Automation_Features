-- Get arguments from command line
on run argv
	if (count of argv) < 3 then
		error "Usage: osascript export_photos.applescript <album_name> <destination_folder> <days>"
	end if
	
	set albumName to item 1 of argv
	set destFolder to item 2 of argv
	set daysBack to (item 3 of argv) as integer
	
	-- Create folder and resolve absolute path
	set destPOSIX to (do shell script "mkdir -p " & quoted form of destFolder & " && cd " & quoted form of destFolder & " && pwd")

tell application "Photos"
	
	-- Get existing files in destination (base names without extensions)
	try
		set existingFiles to do shell script "ls " & quoted form of destPOSIX & " | sed 's/\\.[^.]*$//' | sort -u"
	on error
		set existingFiles to ""
	end try
	
	set allItemsToExport to {}
	
	-- Calculate cutoff date (start of day, daysBack days ago)
	set cutoffDate to (current date) - (daysBack * days)
	-- Set time to start of day (00:00:00)
	set time of cutoffDate to 0
	log "Looking for photos newer than: " & cutoffDate
	
	-- Find the album
	set albs to (every album whose name is albumName)
	log "Found " & (count of albs) & " albums matching '" & albumName & "'"
	
	if (count of albs) > 0 then
		set a to item 1 of albs
		log "Using album: " & (name of a)
		set allItems to media items of a
		log "Album contains " & (count of allItems) & " media items"
		
		-- Count total photos for logging
		set totalPhotos to count of allItems
		set photosInRange to 0
		set photosSkipped to 0
		log "Total photos in album: " & totalPhotos
		
		-- Loop through every photo in the album
		repeat with anItem in allItems
			-- Check if photo is within date range
			-- Try to get the most appropriate date (when photo was taken)
			try
				set photoDate to date of anItem
			on error
				set photoDate to modification date of anItem
			end try
			set photoName to name of anItem
			
			if photoDate ≥ cutoffDate then
				set photosInRange to photosInRange + 1
				-- Skip if it's a movie (so Live Photos won't export the .mov part)
				if (class of anItem as string) is not "movie" then
					set itemFilename to filename of anItem
					-- Remove extension
					set baseName to my removeExtension(itemFilename)
					
					-- Only export if not already present
					if existingFiles = "" or existingFiles does not contain baseName then
						set end of allItemsToExport to anItem
						log "Will export: " & photoName & " (taken: " & photoDate & ")"
					else
						set photosSkipped to photosSkipped + 1
						log "Already exists: " & photoName & " (taken: " & photoDate & ")"
					end if
				end if
			else
				log "Too old: " & photoName & " (taken: " & photoDate & ")"
			end if
		end repeat
		
		log "Photos in date range: " & photosInRange & " out of " & totalPhotos
	else
		log "Album '" & albumName & "' not found!"
		log "Available albums:"
		set allAlbums to every album
		repeat with anAlbum in allAlbums
			log "  - " & (name of anAlbum)
		end repeat
	end if
	
	-- Export new items (images only)
	if (count of allItemsToExport) > 0 then
		export allItemsToExport to (POSIX file destPOSIX as alias) with using originals
		log "Exported " & (count of allItemsToExport) & " new photos from album '" & albumName & "'"
	else
		log "No new photos to export from album '" & albumName & "'"
	end if
end tell

end run

-- Helper function: remove extension
on removeExtension(fileName)
	set AppleScript's text item delimiters to "."
	set nameComponents to text items of fileName
	set AppleScript's text item delimiters to ""
	if (count of nameComponents) > 1 then
		set nameComponents to items 1 thru -2 of nameComponents
		set AppleScript's text item delimiters to "."
		set baseName to nameComponents as string
		set AppleScript's text item delimiters to ""
		return baseName
	else
		return fileName
	end if
end removeExtension