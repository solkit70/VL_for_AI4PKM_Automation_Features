-- Export Apple Notes with metadata to specified folder
-- Usage: osascript export_notes.applescript <destination_folder> <days_back>

on run argv
	if (count of argv) < 2 then
		error "Usage: osascript export_notes.applescript <destination_folder> <days>"
	end if
	
	set destFolder to item 1 of argv
	set daysBack to (item 2 of argv) as integer
	
	-- Create destination folder and resolve absolute path
	set destPOSIX to (do shell script "mkdir -p " & quoted form of destFolder & " && cd " & quoted form of destFolder & " && pwd")
	
	-- Calculate cutoff date (start of day, daysBack days ago)
	set cutoffDate to (current date) - (daysBack * days)
	set time of cutoffDate to 0
	log "Looking for notes newer than: " & cutoffDate
	
	tell application "Notes"
		-- Get recent notes more efficiently by checking modification date first
		set recentNotes to {}
		set notesExported to 0
		set notesSkipped to 0
		
		-- Get all notes but process them more efficiently
		set allNotes to every note
		set totalNotes to count of allNotes
		log "Scanning " & totalNotes & " notes for recent changes..."
		
		-- First pass: quickly filter by modification date (faster than getting full content)
		repeat with aNote in allNotes
			try
				set modDate to modification date of aNote
				set creationDate to creation date of aNote
				
				-- Use the more recent date for filtering (creation or modification)
				set noteDate to creationDate
				if modDate > creationDate then
					set noteDate to modDate
				end if
				
				-- Only add to processing list if within date range
				if noteDate ≥ cutoffDate then
					set end of recentNotes to aNote
				end if
			on error
				-- Skip notes with date access issues
			end try
		end repeat
		
		set recentCount to count of recentNotes
		log "Found " & recentCount & " recent notes to process (skipped " & (totalNotes - recentCount) & " old notes)"
		
		-- Second pass: process only the recent notes
		repeat with aNote in recentNotes
			try
				-- Get note metadata (only for recent notes)
				set noteTitle to name of aNote
				set noteBody to body of aNote
				set creationDate to creation date of aNote
				set modDate to modification date of aNote
				set noteID to id of aNote
				
				-- Use the more recent date (already verified to be recent)
				set noteDate to creationDate
				if modDate > creationDate then
					set noteDate to modDate
				end if
				
				set notesExported to notesExported + 1
				
				-- Format dates for filename and metadata
				set creationDateStr to my formatDate(creationDate)
				set modDateStr to my formatDate(modDate)
				set noteDateStr to my formatDate(noteDate)
				
				-- Create safe filename
				set safeTitle to my sanitizeFilename(noteTitle)
				set fileName to noteDateStr & " " & safeTitle
				
				-- Create metadata JSON
				set metadataJSON to "{" & ¬
					"\"title\": " & my escapeJSON(noteTitle) & "," & ¬
					"\"created\": \"" & creationDateStr & "\"," & ¬
					"\"modified\": \"" & modDateStr & "\"," & ¬
					"\"id\": \"" & noteID & "\"," & ¬
					"\"filename\": " & my escapeJSON(fileName) & ¬
					"}"
				
				-- Save note content (HTML format for better conversion)
				set contentFile to destPOSIX & "/" & fileName & ".html"
				do shell script "echo " & quoted form of noteBody & " > " & quoted form of contentFile
				
				-- Save metadata file
				set metadataFile to destPOSIX & "/" & fileName & ".json"
				do shell script "echo " & quoted form of metadataJSON & " > " & quoted form of metadataFile
				
				log "Exported: " & noteTitle & " (date: " & noteDate & ")"
				
			on error errMsg
				log "Error processing note '" & noteTitle & "': " & errMsg
			end try
		end repeat
		
		log "Export completed: " & notesExported & " notes exported, " & (totalNotes - recentCount) & " skipped (too old)"
		
	end tell
end run

-- Helper function: format date as YYYY-MM-DD
on formatDate(dateObj)
	try
		set y to year of dateObj
		set m to month of dateObj as integer
		set d to day of dateObj
		set monthStr to text -2 thru -1 of ("0" & m)
		set dayStr to text -2 thru -1 of ("0" & d)
		return (y as string) & "-" & monthStr & "-" & dayStr
	on error
		-- Fallback to current date if there's an issue
		set currentDate to current date
		set y to year of currentDate
		set m to month of currentDate as integer
		set d to day of currentDate
		set monthStr to text -2 thru -1 of ("0" & m)
		set dayStr to text -2 thru -1 of ("0" & d)
		return (y as string) & "-" & monthStr & "-" & dayStr
	end try
end formatDate

-- Helper function: sanitize filename
on sanitizeFilename(str)
	-- Replace problematic characters with safe alternatives
	set str to my replaceText(str, "/", "-")
	set str to my replaceText(str, "\\", "-")
	set str to my replaceText(str, ":", "-")
	set str to my replaceText(str, "*", "-")
	set str to my replaceText(str, "?", "-")
	set str to my replaceText(str, "\"", "-")
	set str to my replaceText(str, "<", "-")
	set str to my replaceText(str, ">", "-")
	set str to my replaceText(str, "|", "-")
	set str to my replaceText(str, "  ", " ") -- Replace double spaces
	
	-- Trim and limit length
	set str to my trimText(str)
	if length of str > 100 then
		set str to text 1 thru 100 of str
	end if
	
	return str
end sanitizeFilename

-- Helper function: escape JSON strings
on escapeJSON(str)
	set str to my replaceText(str, "\\", "\\\\")
	set str to my replaceText(str, "\"", "\\\"")
	set str to my replaceText(str, return, "\\n")
	set str to my replaceText(str, tab, "\\t")
	return "\"" & str & "\""
end escapeJSON

-- Helper function: replace text
on replaceText(str, oldText, newText)
	set AppleScript's text item delimiters to oldText
	set textItems to text items of str
	set AppleScript's text item delimiters to newText
	set newStr to textItems as string
	set AppleScript's text item delimiters to ""
	return newStr
end replaceText

-- Helper function: trim whitespace
on trimText(str)
	repeat while str starts with " " or str starts with tab or str starts with return
		set str to text 2 thru -1 of str
	end repeat
	repeat while str ends with " " or str ends with tab or str ends with return
		set str to text 1 thru -2 of str
	end repeat
	return str
end trimText

-- Helper function: convert list to string
on listToString(lst, delimiter)
	set AppleScript's text item delimiters to delimiter
	set str to lst as string
	set AppleScript's text item delimiters to ""
	return str
end listToString
