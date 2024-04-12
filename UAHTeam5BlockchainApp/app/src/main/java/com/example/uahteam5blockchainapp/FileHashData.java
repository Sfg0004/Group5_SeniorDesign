package com.example.uahteam5blockchainapp;

public class FileHashData
{
    private String fileName;        //String to hold the name of the file
    private String fileHash;        //String to hold the file's hash

    public void setFileName(String newFileName)
    {
        fileName = newFileName;
    }

    public void setFileHash(String newFileHash)
    {
        fileHash = newFileHash;
    }
}
