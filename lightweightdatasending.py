elif lwMsg == "Upload_File":
	localHash = comm.receivedatafromrequester(lw1)
	localFileName = comm.receivedatafromrequester(lw1)
	localAuthor = comm.receivedatafromrequester(lw1)
	localAccessList = comm.receivedatafromrequester(lw1)
	newBlockToAdd = FileData(localHash, localFileName, localAuthor, localAccessList)
        lwMsg = " "
elif lwMsg == "Download_File":
	authorizingUser = comm.receivedatafromrequester(lw1)
	localHash = comm.receivedatafromrequester(lw1)
	localFileName = comm.receivedatafromrequester(lw1)
	localAuthor = comm.receivedatafromrequester(lw1)
	localAccessList = comm.receivedatafromrequester(lw1)
	newBlockToAdd = FileData(localHash, localFileName, localAuthor, localAccessList)
        lwMsg = " "

elif lwMsg == "Create_User":
	authorizingUser = comm.receivedatafromrequester(lw1)
	localUsername = comm.receivedatafromrequester(lw1)
	localPassword = comm.receivedatafromrequester(lw1)
	localRole = comm.receivedatafromrequester(lw1)
	localLegalName = comm.receivedatafromrequester(lw1)
	newBlockToAdd = Account(localUsername, localPassword, localRole, localLegalName)
        lwMsg = " "
        #lwBlock = comm.receivedatafromrequester(lw1)
        #returnedLW = convertBlock(lwBlock)
        #lw_to_full.put(returnedLW)
        lwMsg = " "
time.sleep(0.2)

#The only thing to do handle the new block from the passed data

#Note, I close the socket afterwards. Should I just keep it open?
