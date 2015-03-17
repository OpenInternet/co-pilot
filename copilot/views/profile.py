#Get application content
from copilot import app, db, models
from copilot.models import get_valid_actions, get_valid_targets
from copilot.views import forms
from flask.ext.wtf import Form

#Get flask modules
from flask import redirect, url_for, render_template, flash
from flask.ext.login import login_user, login_required
from wtforms import FormField
from copilot.controllers import get_trainer

@app.route('/profile/new', methods=["GET", "POST"])
@login_required
def profile_new():
    """Display an empty profile editor."""
    form = forms.NewProfileForm()
    if form.validate_on_submit():
        profile = models.Profile(form.data['prof_name'])
        for rule in form.data['rules']:
            _rule = models.Rule(rule['target'], rule['action'], rule['sub_target'])
            profile.add_rule(_rule)
        profile.save()
        #Save as current profile for trainer.
        trainer = get_trainer()
        trainer.current = form.data['prof_name']
        db.session.commit()
        profile.apply_it()
        flash('Your profile has been saved and Applied!')
        return redirect(url_for('profile_applied'))
    else:
        profile = models.Profile("new")
        profile.save()
        form.rules.append_entry(data={"target":"dns", "sub_target":"foxnews.com", "action":"block"})
        return render_template('prof_new.html', form=form)


@app.route('/profile/edit/<string:prof_name>', methods=["GET", "POST"])
@login_required
def profile_edit(prof_name):
    """Display an existing profle in the profile editor."""
    form = forms.ProfileForm()
    if form.validate_on_submit():
        profile = models.Profile(prof_name)
        for rule in form.data['rules']:
            _rule = models.Rule(rule['target'], rule['action'], rule['sub_target'])
            profile.add_rule(_rule)
        profile.save()
        #Save as current profile for trainer.
        trainer = get_trainer()
        trainer.current = prof_name
        db.session.commit()
        profile.apply_it()
        flash('Your profile has been saved and Applied!')
        return redirect(url_for('profile_applied'))
    else:
        profile = models.Profile(prof_name)
        if profile.exist():
            profile.load()
        else:
           return redirect(url_for('profile_new'))
    form.name = prof_name
    for rule in profile.rules:
        form.rules.append_entry(data={"target":rule.target, "sub_target":rule.sub_target, "action":rule.action})

    return render_template('profile_edit.html', form=form)

@app.route('/profile/applied', methods=["GET", "POST"])
@login_required
def profile_applied():
    """Display an empty profile editor."""
    #Check for profile_edit
    trainer = get_trainer()
    #populate from trainer if possible
    prof_applied = trainer.current
    print(prof_applied)
    # if none send trainer to create a new one.
    if prof_applied == None:
        return redirect(url_for('profile_new'))
    profile = models.Profile(prof_applied)
    profile.load()
    return render_template('profile_applied.html', profile=profile)

@app.route('/profile/save', methods=["GET", "POST"])
@login_required
def profile_save():
    """Display the profile that is currently being run on the Co-Pilot box. """

    return render_template('profile_save.html', form=form)

@app.route('/profile/load', methods=["GET", "POST"])
@login_required
def profile_load():
    """Display the profile that is currently being run on the Co-Pilot box. """

    return render_template('profile_load.html', form=form)

@app.route('/profile/current', methods=["GET", "POST"])
@login_required
def profile_current():
    """Display the profile that is currently being run on the Co-Pilot box. """

    return render_template('profile_current.html', form=form)
