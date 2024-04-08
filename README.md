Since it's likely people will be working on the same parts of this project, we'll be using the test branch as a psuedo-main so that we can resolve conflicts and get our code in one place before committing to main. Hopefully we can avoid what happened last time with this

To do work, make sure to create your own branch with your name on it and do all your work only on that. You can do this here on the deskptop app: 

![image](https://github.com/S1edgehammer500/SD/assets/124877607/36f09bad-7201-4bf9-89ee-8ef2ee7d8761)

Make sure everything you've done is working before pushing it to origin and making a pull request.
Before starting any work, make sure you have merged test with your own branch, like this:

![image](https://github.com/S1edgehammer500/SD/assets/124877607/e4f10a0b-81d0-45c6-b6dd-a73fd334742e)

When you make a pull request, do this to change the branch you are merging to to test:

![image](https://github.com/S1edgehammer500/SD/assets/124877607/668ec766-d23a-4117-a54a-fbce95b50b49)

Resolve any conflicts and once we all agree that we have completed a section i.e. crud for restaurants, one person can merge test to main and then we will all click 'pull origin' and merge main into our branches.

By doing this, if an issue like last time comes up, only test will be incorrect and main should be okay. Generally it's good practice to let others review your pull request before merging but since we aren't merging to main, as long as what you have is working, it should be fine to go ahead and merge your pull request to test

Try and co-ordinate a bit with people working on the same files as you though, for example, earlier today I only worked in UserModel.py and Luqmaan only worked in routes.py and we didn't touch the other files. If we wanted something changed, we just told the other to change it on their branch. This should decrease the amount of conflicts which should also decrease the room for error

Also discard all changes to pycache files or the database before committing. If the changed file has this screen, discard it:

![image](https://github.com/S1edgehammer500/SD/assets/124877607/811385d9-e387-4091-893e-5cfdb60550a2)

Finally, you can run the code by pressing run in `routes.py`. You can sign in to an admin profile with the username 'Jake' and password 'England'


