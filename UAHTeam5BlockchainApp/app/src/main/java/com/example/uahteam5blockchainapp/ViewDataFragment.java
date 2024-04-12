package com.example.uahteam5blockchainapp;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.Gravity;
import android.view.ViewGroup;
import androidx.annotation.NonNull;
import androidx.fragment.app.Fragment;
import androidx.navigation.fragment.NavHostFragment;

import com.example.uahteam5blockchainapp.databinding.FragmentViewdataBinding;
public class ViewDataFragment extends Fragment
{
    private PythonCode tempCaller;      //Python function caller code
    private FragmentViewdataBinding binding;

    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState)
    {
        binding = FragmentViewdataBinding.inflate(inflater, container, false);
        Bundle arguments = getArguments();      //Gets the arguments from the previous Fragment
        //If there is an argument and the arguments contains the desired text
        if (arguments != null && arguments.containsKey("textToDisplay"))
        {
            //Gets the passed string from the arguments
            binding.Content.setText(arguments.getString("textToDisplay"));
        }
        //If there is an argument and the arguments contains the desired text for the title
        if (arguments != null && arguments.containsKey("title"))
        {
            //Gets the passed string title from the arguments
            binding.ContentDescription.setText(arguments.getString("title"));
        }
        //If the view is displaying the active users, increase the font size
        if ((binding.ContentDescription.getText()).equals("Active Users"))
        {
            //Increases the font size
            binding.Content.setTextSize(20);
            //Centers the text
            binding.Content.setGravity(Gravity.CENTER);
        }

        //Handles what happens when the user presses the done button
        binding.Done.setOnClickListener(new View.OnClickListener() {

            @Override
            public void onClick(View view)
            {
                //Navigates back to the admin Fragment
                NavHostFragment.findNavController(ViewDataFragment.this).navigate(R.id.action_ViewDataFragment_to_AdminFragment);
            }
        });
        return binding.getRoot();
    }

    public void onViewCreated(@NonNull View view, Bundle savedInstanceState)
    {
        super.onViewCreated(view, savedInstanceState);
    }

    @Override
    public void onDestroyView() {
        super.onDestroyView();
        binding = null;
    }
}
