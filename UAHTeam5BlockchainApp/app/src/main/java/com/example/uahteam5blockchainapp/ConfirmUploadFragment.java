package com.example.uahteam5blockchainapp;

import android.Manifest;
import android.content.DialogInterface;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.appcompat.app.AlertDialog;
import androidx.fragment.app.Fragment;
import androidx.navigation.fragment.NavHostFragment;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStream;
import java.io.StreamCorruptedException;
import java.net.URI;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.Toast;

import com.example.uahteam5blockchainapp.databinding.FragmentUploadConfirmBinding;

public class ConfirmUploadFragment extends Fragment
{
    private int DefaultColor = 0;       //Variable to hold the default color for the list of buttons
    Uri uploadResource;     //Resource that will be send onto the blockchain
    private FragmentUploadConfirmBinding binding;       //Binding to refer to the current fragment
    private PythonCode tempCaller;      //Python function caller code
    private ArrayList<String> usersToGiveAccess;        //ArrayList of users to give access to

    private ActivityResultLauncher<String[]> requestPermissionLauncher = registerForActivityResult(new ActivityResultContracts.RequestMultiplePermissions(), permissions ->
    {
        //If permission is granted to read and write files, do nothing
        if (permissions.getOrDefault(android.Manifest.permission.READ_EXTERNAL_STORAGE, false) && permissions.getOrDefault(Manifest.permission.WRITE_EXTERNAL_STORAGE, false)) {
            Toast.makeText(getContext(), "Permission granted to read and write to files", Toast.LENGTH_SHORT).show();
        }
    });

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        binding = FragmentUploadConfirmBinding.inflate(inflater, container, false);
        Bundle arguments = getArguments();      //Gets the arguments from the previous Fragment
        //If there was an argument provided and there is a uri in it, get the URI as a string and then parse it into a Uri objec
        if (arguments != null && arguments.containsKey("uri"))
        {
            //Process the Uri to determine its type
            uploadResource = Uri.parse(arguments.getString("uri"));
            //Toast.makeText(getContext(), uploadResource.toString(), Toast.LENGTH_LONG).show();
            String UriType = uploadResource.getScheme();

            binding.usersToGiveAccessToText.setVisibility(View.VISIBLE);       //Sets the image to the image given
            //If the file is a picture, change the image and the text description
            if (uploadResource.getPath().toLowerCase(Locale.US).endsWith(".png"))
            {
                binding.imageImportImage.setImageURI(uploadResource);       //Sets the image to the image given
                binding.imageImportText.setText(uploadResource.getLastPathSegment());       //Gets the filename of the Uri
                binding.imageImportImage.setVisibility(View.VISIBLE);      //Makes the view visible
                binding.imageImportText.setVisibility(View.VISIBLE);       //Makes the text view visible
            }
            //Else, determine the file type and make the image as determined
            else
            {
                //Switches to change the displayed image based on the given Uri
                switch (UriType)
                {
                    //If file Uri, make the image look like a single file with the file name
                    case "file":
                        binding.fileImportText.setText(uploadResource.getLastPathSegment());         //Sets the description for the image
                        binding.fileImportImage.setVisibility(View.VISIBLE);      //Makes the image view visible
                        binding.fileImportText.setVisibility(View.VISIBLE);       //Makes the text view visible
                        break;
                    //If file Uri, make the image look like a single file with the file name
                    case "content":
                        binding.folderImportText.setText(uploadResource.getLastPathSegment());         //Sets the description for the image
                        binding.folderImportImage.setVisibility(View.VISIBLE);     //Makes the view visible
                        binding.folderImportText.setVisibility(View.VISIBLE);      //Makes the text view visible
                        break;
                    //At the moment, there is no plan for any other image, so the default is to have a file folder displayed
                    default:
                        binding.fileImportText.setText(uploadResource.getLastPathSegment());         //Sets the description for the image
                        binding.fileImportImage.setVisibility(View.VISIBLE);       //Makes the view visible
                        binding.fileImportText.setVisibility(View.VISIBLE);        //Makes the view visible
                }
            }
            //Creates the PythonCode object to upload files
            tempCaller = PythonCode.PythonCode(getContext());
            //Gets the list of active users
            ArrayList<String> activeUsers = tempCaller.getListActiveUsers();
            //Creates an ArrayList of the users to give access to
            usersToGiveAccess = new ArrayList<>();

            //Gets the linear layout for this fragment
            LinearLayout linearLayout = binding.UsersToGiveAccessTo;
            //Loops through all usernames and adds a button for each
            for (int i = 0; i < activeUsers.size(); i++)
            {
                //Creates a new button
                Button newButton = new Button(requireContext());
                //Creates a temp string to save the current file name
                String tempName = activeUsers.get(i);
                //Sets the text of the button to the name of the file
                newButton.setText(activeUsers.get(i));
                //Sets the background for the new button
                newButton.setBackgroundResource(R.drawable.ripple_button);
                //Handles what happens when the button is pressed
                newButton.setOnClickListener(new View.OnClickListener()
                {
                    //Determines what happens when the button is clicked
                    @Override
                    public void onClick(View view)
                    {
                        //Checks if the button has been pressed already, i.e. the current color is blue
                        if (newButton.isSelected())
                        {
                            newButton.setSelected(false);
                            //Change the color to default
                            newButton.setBackgroundColor(Color.parseColor("#D3D3D3"));
                            //Removes the username from the list of users to give access to
                            usersToGiveAccess.remove(tempName);
                        }
                        //Else, the button has not been pressed already
                        else
                        {
                            newButton.setSelected(true);
                            //Changes the color of the button to show it has been selected
                            newButton.setBackgroundColor(Color.parseColor("#0077C8"));
                            //Adds the username to give access to to the list of users
                            usersToGiveAccess.add(tempName);
                        }
                    }
                });
                //Adds the new button to the linear layout
                linearLayout.addView(newButton);
            }
        }
        return binding.getRoot();
    }

    @Override
    public void onViewCreated(View view, Bundle savedInstanceState)
    {
        //Creates a little screen to show the file is being uploaded
        //progressDialog = new ProgressDialog(getContext());


        //If button pressed, send control back to the first fragment
        binding.CancelUpload.setOnClickListener(new View.OnClickListener()
        {
            //Overrides the action when the button is pressed
            @Override
            public void onClick(View view)
            {
                //Confirms the user wants to cancel the upload
                confirmCancel();
            }
        });

        //Function to handle when the upload from device button is selected
        binding.ConfirmUpload.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view)
            {
                //If no users have been selected to have access
                if (usersToGiveAccess.isEmpty())
                {
                    //Alert and inform the user that they need to select users to give access to
                    alertUser();
                    return;     //Exits the function
                }
                //Else, users have been selected to get access to the function
                //Starts the upload process
                //Updates the blockchain
                tempCaller.refreshBlockchain();
                //Gets a list of the files already on the blockchain
                ArrayList<String> filesOnBlockchain = tempCaller.listFiles();

                //Creates a new file object to point to the resource to upload
                File newFile = new File(uploadResource.getPath());
                //If the file is already on the blockchain
                if (filesOnBlockchain.contains(newFile.getName()))
                {
                    //At this point, could append(1) to the file name and change its name for uploading
                    //Informs the user of the duplicate nature of the file
                    duplicateAlert();
                    uploadResource = null;
                    //Now, proceed back to the First Fragment
                    NavHostFragment.findNavController(ConfirmUploadFragment.this).navigate(R.id.action_ConfirmUploadFragment_to_FirstFragment);
                }
                //Else, the file is not already uploaded to the blockchain
                else
                {
                        byte[] uploadBytes = getUploadBytes();
                        //If the upload bytes is an issue, exit
                        if (uploadBytes == null)
                        {
                            //Should not happen. But, if it does, log it
                            Log.e("File Upload Error", "Cannot Upload'" + uploadResource.getPath() + "' to the blockchain as it is null");
                            uploadResource = null;
                            //Now, proceed back to the First Fragment
                            NavHostFragment.findNavController(ConfirmUploadFragment.this).navigate(R.id.action_ConfirmUploadFragment_to_FirstFragment);
                        }
                        StringBuilder basicString = new StringBuilder();
                        for (int i = 0; i < usersToGiveAccess.size(); i++)
                        {
                            basicString.append(usersToGiveAccess.get(i));
                            if (i != usersToGiveAccess.size()-1)
                            {
                                basicString.append('/');
                            }
                        }
                        //String[] array = usersToGiveAccess.toArray(new String[0]);
                        Log.e("Uploading File", "Uploading " + newFile.getName() + " from " + newFile.getPath());
                        //Calls the uploadIpfs() function in Python and sends it the login arguments and returns the result
                        String resultingHash = tempCaller.uploadFile(uploadBytes, uploadResource.getPath(), newFile.getName(), basicString.toString());
                        Log.e("Uploading File", "Uploading " + newFile.getName() + " from " + newFile.getPath());
                        //After uploading, the blockchain is refreshed automatically
                        uploadResource = null;

                        UploadFinishFragment newFragment = new UploadFinishFragment();        //Creates the next fragment variable
                        Bundle newArguments = new Bundle();        //Creates a new bundle of arguments to send
                        newArguments.putString("filehash", resultingHash);  //Adds the uri to the bundle///////////////takenImage.toString()(or.toPath)
                        newFragment.setArguments(newArguments);        //Sends the arguments to the next fragment
                        //Now, proceed to the Upload finish Fragment
                        NavHostFragment.findNavController(ConfirmUploadFragment.this).navigate(R.id.action_ConfirmUploadFragment_to_UploadFinishFragment, newArguments);

                    /*
                    //Catches an input exception
                    catch (Exception error)
                    {
                        Log.e("errorMessage", Arrays.toString(error.getStackTrace()));
                        //Should not happen. But, if it does, log it
                        Log.e("File Upload Error", "Cannot Upload'" + uploadResource.getPath() + "' to the blockchain");
                        uploadResource = null;
                        //Now, proceed back to the First Fragment
                        NavHostFragment.findNavController(ConfirmUploadFragment.this).navigate(R.id.action_ConfirmUploadFragment_to_FirstFragment);
                    }*/
                }
            }
        });

    }


    //Function to alert the user so they know the file already exists on the blockchain
    private void duplicateAlert()
    {
        //Creates an alert dialog to inform the user
        AlertDialog.Builder builder = new AlertDialog.Builder(getContext());
        builder.setTitle("");
        builder.setMessage("File already exists on the blockchain");
        //Creates the button to for the acknowledgement action
        builder.setPositiveButton("Ok", new DialogInterface.OnClickListener()
        {
            public void onClick(DialogInterface logoutDialog, int ID)
            {
                //Dismisses the logout dialog box
                logoutDialog.dismiss();
            }
        });
        //Creates the dialog box
        AlertDialog logoutDialog = builder.create();
        //Shows the dialog box
        logoutDialog.show();
    }

    //Function to alert the user that they need to select users to give users access
    private void alertUser()
    {
        //Creates an alert dialog to inform the user
        AlertDialog.Builder builder = new AlertDialog.Builder(getContext());
        builder.setTitle("");
        builder.setMessage("Select the user(s) to give access to");
        //Creates the button to for the acknowledgement action
        builder.setPositiveButton("Ok", new DialogInterface.OnClickListener()
        {
            public void onClick(DialogInterface logoutDialog, int ID)
            {
                //Dismisses the logout dialog box
                logoutDialog.dismiss();
            }
        });
        //Creates the dialog box
        AlertDialog logoutDialog = builder.create();
        //Shows the dialog box
        logoutDialog.show();
    }

    //Function to confirm the user wants to logout
    private void confirmCancel()
    {
        //Creates an alert dialog to show that
        AlertDialog.Builder builder = new AlertDialog.Builder(getContext());
        builder.setTitle("Cancel Upload");
        builder.setMessage("Are you sure you want to cancel?");
        //Creates two buttons
        //Creates the button to for the positive action
        builder.setPositiveButton("Yes", new DialogInterface.OnClickListener()
        {
            public void onClick(DialogInterface logoutDialog, int ID)
            {
                uploadResource = null;
                //Navigate back to the first Fragment
                NavHostFragment.findNavController(ConfirmUploadFragment.this).navigate(R.id.action_ConfirmUploadFragment_to_FirstFragment);
            }
        });
        //Creates the button to for the positive action
        builder.setNegativeButton("No", new DialogInterface.OnClickListener()
        {
            public void onClick(DialogInterface logoutDialog, int ID)
            {
                //Do nothing, but dismisses the dialog box
                logoutDialog.dismiss();
            }
        });
        //Creates the dialog box
        AlertDialog logoutDialog = builder.create();
        //Shows the dialog box
        logoutDialog.show();
    }

    //Function to handle the saving of the URI
    //Returns the path to the destination file
    private byte[] getUploadBytes()
    {
        //Gets the directory of the files
        File baseDirectory = requireContext().getExternalFilesDir(null);
        File directory = new File(baseDirectory + "/uploadedFiles/");
        //If the directory does not exist, create it
        if (!directory.exists())
        {
            //Create the directory
            directory.mkdirs();
            //If it still does not exist, something major went wrong
            if (!directory.exists())
            {
                //Directory creation failed
                Log.e("DirMakeError", "Failed to create directory");
            }
        }
        Log.e("File to upload", uploadResource.getPath());
        String UriType = uploadResource.getScheme();
        //If there is something to the the URI, then proceed with the program
        if (UriType != null && uploadResource != null)
        {
            //Now, copy the file from the source directory to the destination
            try
            {
                //Opens an input stream and passes it through several containers to get the final product
                InputStream inputStream = requireContext().getContentResolver().openInputStream(uploadResource);
                ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();
                byte[] tempBytes = new byte[4096];
                int numBytesRead = inputStream.read(tempBytes);
                while (numBytesRead != -1)
                {
                    byteArrayOutputStream.write(tempBytes, 0, numBytesRead);
                    numBytesRead = inputStream.read(tempBytes);
                }
                inputStream.close();
                return byteArrayOutputStream.toByteArray();
                //oldcode34
            }
            //Catches the potential exception
            catch (IOException error)
            {
                Toast.makeText(getContext(), "Error when copying file data", Toast.LENGTH_LONG).show();
                Log.e("Termination Error", Arrays.toString(error.getStackTrace()));
                throw new RuntimeException();   //Throws an exception to terminate the program as this should never happen
            }
        }
        //Else, null, so log
        //Should not happen
        else
        {
            Log.e("null resource", "null resource to upload");
            return null;
        }
    }



    //Function to read and returns the Uris from the given file
    public ArrayList<URI> readUrisFromFile(String filename)
    {
        ArrayList<URI> UriList = new ArrayList<URI>();      //Creates a new ArrayList for the Uris
        try
        {
            //Create new file and buffer reader to process the file
            FileReader fileReader = new FileReader(filename);
            BufferedReader bufferedReader = new BufferedReader(fileReader);
            String UriLine = bufferedReader.readLine();     //Reads the first line from the file
            //Loops through the entire file and collects the Uris
            while (UriLine != null)
            {
                UriList.add(URI.create(UriLine));       //Adds the new URI to the end of the list
                UriLine = bufferedReader.readLine();     //Reads the next line from the file
            }
            //Closes the connection to the file handlers
            fileReader.close();
            bufferedReader.close();
        }
        //Catches an exception with reading the file
        catch (IOException error)
        {
            Toast.makeText(getContext(), "Runtime exception", Toast.LENGTH_LONG).show();
            throw new RuntimeException();       //Throws an exception as an error occurred
        }
        return UriList;     //Returns the list of URIs
    }

    //Function to read and returns the Uris from the given file
    public void writeUrisToFile(String filename, ArrayList<URI> UriList)
    {
        //Tries to write the given Uris to the file
        try
        {
            //Creates a file writer and buffered writer to write to the file
            FileWriter fileWriter = new FileWriter(filename);
            BufferedWriter bufferedWriter = new BufferedWriter(fileWriter);
            //Loops through the entire Uri list and writes them to the file
            for (int i = 0; i < UriList.size(); i++)
            {
                bufferedWriter.write(UriList.get(i).toString() + "\n");
            }
            //Closes the connection to the file handlers
            bufferedWriter.close();
            fileWriter.close();
        }
        //Catches an exception with writing to the file
        catch (IOException error)
        {
            throw new RuntimeException();       //Throws an exception as an error occurred
            //In the future, maybe add a toast message and send back to the upload fragment
        }
    }

    //Function to destroy the view and delete the view elements when it is left
    @Override
    public void onDestroyView()
    {
        super.onDestroyView();
        binding = null;
    }
}
/*

old code



                //Creates a new file output stream to append the new Uri to
                //FileInputStream sourceFile = new FileInputStream(uriFile.getPath());
                //Creates a new file output stream to append the new Uri to
                //FileOutputStream destinationFile = new FileOutputStream(destFile);
                //Creates a buffer to hold the input data
                //byte[] bufferReader = new byte[1024];
                //int lengthOfInputData = sourceFile.read(bufferReader);
                //Loops through the entire file to read the contents
                //while (lengthOfInputData > 0)
                //{
                    //Writes the data to the file
                //    destinationFile.write(bufferReader, 0, lengthOfInputData);
                    //Reads the next data set
                //    lengthOfInputData = sourceFile.read(bufferReader);
                //}
                //Closes the file streams
                //destinationFile.close();
                //sourceFile.close();
                return saveFilename;



/*
            //For simplicity for the download fragment, might need to organize the file here
            ArrayList<URI> UriList = readUrisFromFile(filename);

            //Compare file Uris and sort them


            writeUrisToFile(filename, UriList);     //Writes the sorted Uris to the given file

 */
/*


                        //File newFile2 = new File(uploadResource.getPath());

                        Toast.makeText(getContext(), filePath, Toast.LENGTH_LONG).show();
                        //Creates a new handler for the input file stream using the file path of the resource
                        FileInputStream fileInputStream = new FileInputStream(filePath);
                        //Creates a new collection of bytes to hold the result
                        ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();
                        //Creates a new byte array 1024 bites long
                        byte[] buffer = new byte[1024];
                        //Variable holding the bytes read
                        int bytesRead = fileInputStream.read(buffer);
                        //Loops through all data in the file
                        while (bytesRead != -1)
                        {
                            //Writes the bytes to the byte output stream
                            byteArrayOutputStream.write(buffer, 0, bytesRead);
                            //Loads the next set of data
                            Log.e("File Upload Error6", "Cannot Upload'" + filePath + "' to the blockchain");
                            bytesRead = fileInputStream.read(buffer);
                        }
                        //Converts the content into an array of bytes
                        byte[] fileContentToUpload = byteArrayOutputStream.toByteArray();
                        //Closes the file input stream
                        fileInputStream.close();
                        //Closes the byte array output stream
                        byteArrayOutputStream.close();

 */
/*

                    //Invokes the python code to upload the given file with its name
                    //boolean conclusion =
                    //If upload was a success, move onto the next fragment
                    if (tempCaller.uploadFile(getContext(), uploadResource.getPath(), newFile.getName()))
                    {
                        //Now, proceed back to the Upload finish Fragment
                        NavHostFragment.findNavController(ConfirmUploadFragment.this).navigate(R.id.action_ConfirmUploadFragment_to_UploadFinishFragment);
                    }
                    //Else, the file upload failed, so alert the user
                    else
                    {
                        //Informs the user of the failure to upload the file
                        Toast.makeText(getContext(), "Failed to upload to blockchain", Toast.LENGTH_LONG).show();
                        //Now, proceed back to the First Fragment
                        NavHostFragment.findNavController(ConfirmUploadFragment.this).navigate(R.id.action_ConfirmUploadFragment_to_FirstFragment);
                    }

                    NavHostFragment.findNavController(ConfirmUploadFragment.this).navigate(R.id.action_ConfirmUploadFragment_to_FirstFragment);
                    */
//oldcode34
/*

    InputStreamReader inputStreamReader = new InputStreamReader(inputStream);
    BufferedReader bufferedReader = new BufferedReader(inputStreamReader);
    //String variable to hold the line-by-line content from the file
    String line;
    //New string builder to contain the line by line data
    StringBuilder stringBuilder = new StringBuilder();
//Reads the first line
                line = bufferedReader.readLine();
                        //Loops through the entire file
                        while (line != null)
                        {
                        //Adds the current line to the string builder
                        stringBuilder.append(line);
                        //Reads the next line from the file
                        line = bufferedReader.readLine();
                        }
                        //Closes the input stream
                        inputStream.close();
                        inputStreamReader.close();
                        bufferedReader.close();

                        //Returns the bytes of the string from the UTF-8 format
                        return (stringBuilder.toString()).getBytes(StandardCharsets.UTF_8);*/