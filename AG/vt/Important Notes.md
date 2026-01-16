Note (Backend Logic) :

1. There are four flows we need to follow for the feature development of the virtual tagging. 
2. First there is a flow of user addition of the cloud account (new), then we have to schedule the process to our existing infra/ addition of the services to 
    our infra, and we can proceed with the flow suggested above.
3. Second, there is a flow if we have a existing user, he has a existing cloud account then we have to run the manual trigger to the cron job first, from 
    admin site as discussed, and he will be getting the flow as expected.
4. Third, there is a addition of a resource to their cloud account itself, this means is the cloud account the user has added, has the additions
     of the resources or instances. Resource observer or some other similar service will accommodate the resource changes and that will make the
     Virtual Observer notice that, there is a addition or some changes...
5. Fourth, There is a manual addition of the virtual tag then we have to proceed with the appending of the virtual tags to the existing of the virtual tags 
    or the addition of the virtual tags specified by the user (manually added).
   

Note (Frontend Logic) :

There can be many ways to call the API  from user interface:

1. It maybe called right after the addition of cloud account after a particular time period. 
2. We can estimate the time period after the calculations might be done, then we fetch first,
    if data retrieved, we can just omit calling, if not then it can be polled after a certain duration (eg. 15 mins, 30 mins etc.)
3. We can show user to wait till that point of time, then we might can just follow the approaches/ best practices to 
    fetch the data that is being called. 
4. It can be polled right after the addition of the cloud account till the time we did not get the data to the user interface for the first time itself.






 