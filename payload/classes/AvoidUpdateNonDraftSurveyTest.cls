/*Test for the AvoidUpdateNonDraftSurvey Trigger
* (c) Copyright 2013 Grameen Foundation USA. All rights reserved
*/
@isTest
private class   AvoidUpdateNonDraftSurveyTest {

    static testMethod void VerifySurveyStatusInsertScoringGroup() {
        // create a new ScoringGroup__c
        Survey__c survey = new Survey__c(Name='survey');
        insert survey;
        //insert a ScoringGroup
        ScoringGroup__c scoringGroup = new ScoringGroup__c(Caption__c ='TestscoringGroup', Survey__c=survey.Id);
        insert scoringGroup;
        //ASSERTIONS
        List<SurveyVersion__c> versions = [select Version__c, Status__c,Name from SurveyVersion__c where Survey__r.Id = :survey.Id];
        survey = [select Status__c from Survey__c where Id=:survey.Id];
        system.assertEquals(1, versions.size());
        system.assertEquals(SurveyDO.STATUS_DRAFT,survey.Status__c);
        versions[0].Status__c = SurveyDO.STATUS_PUBLISHED;
        update versions;
        //try to insert a new scoringGroup,it should fail since Survey is Published

        ScoringGroup__c newscoringGroup = new ScoringGroup__c(Caption__c ='TestscoringGroup2', Survey__c=survey.Id);
        try{
            insert newscoringGroup;
            system.assert(false);
        }catch(Exception e){
            system.assert(true);
        }

        //try to update a ScoringGroup,it should fail since Survey is Published

        try{
            update scoringGroup;
            system.assert(false);
        }catch(Exception e){
            system.assert(true);
        }


    }
}