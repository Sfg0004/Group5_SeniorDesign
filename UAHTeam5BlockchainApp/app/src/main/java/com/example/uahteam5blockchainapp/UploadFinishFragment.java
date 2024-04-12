package com.example.uahteam5blockchainapp;

import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Toast;
import androidx.fragment.app.Fragment;
import androidx.navigation.fragment.NavHostFragment;

import com.example.uahteam5blockchainapp.databinding.FragmentUploadFinishBinding;



public class UploadFinishFragment extends Fragment
{
    private FragmentUploadFinishBinding binding;

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        binding = FragmentUploadFinishBinding.inflate(inflater, container, false);
        return binding.getRoot();
    }

    @Override
    public void onViewCreated(View view, Bundle savedInstanceState)
    {
        //Function to handle when the user selects the copy hash button
        binding.copyButton.setOnClickListener(new View.OnClickListener()
        {
            //Copies the text in the text box to the clipboard
            @Override
            public void onClick(View view)
            {
                //Gets the hash from the text view
                String fileHash = binding.hashtextview.getText().toString();
                //Creates a new clipboard manager object
                ClipboardManager clipboard = (ClipboardManager) requireActivity().getSystemService(Context.CLIPBOARD_SERVICE);
                //Creates a new clip with the file hash
                ClipData clip = ClipData.newPlainText("Blockchain file hash", fileHash);
                //Sets the primary clip text to the file hash
                clipboard.setPrimaryClip(clip);
                //Makes a toast message to inform the user that the hash has been copied to the clipboard
                Toast.makeText(getContext(), "Hash copied to clipboard", Toast.LENGTH_LONG).show();
            }
        });

        //Function to handle when the user selects the copy hash button
        binding.Continue.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view)
            {
                //Proceeds onto the first fragment
                NavHostFragment.findNavController(UploadFinishFragment.this).navigate(R.id.action_UploadFinishFragment_to_FirstFragment);
            }
        });
    }

    //Function to destroy the view and delete the view elements when it is left
    @Override
    public void onDestroyView()
    {
        super.onDestroyView();
        binding = null;
    }
}
