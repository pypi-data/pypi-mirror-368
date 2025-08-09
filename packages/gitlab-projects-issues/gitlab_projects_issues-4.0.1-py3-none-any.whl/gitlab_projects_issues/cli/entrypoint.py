#!/usr/bin/env python3

# Standard libraries
from argparse import Namespace
from enum import Enum
from typing import Dict, List, Optional, Union
import urllib.parse

# Modules libraries
from gitlab.config import ConfigError, GitlabConfigParser
from gitlab.exceptions import (
    GitlabGetError, )
from gitlab.v4.objects import (
    Project as GitLabProject,
    ProjectMilestone,
)

# Components
from ..features.gitlab import GitLabFeature
from ..types.milestones import MilestoneDescription
from ..types.statistics import AssigneeStatistics, MilestoneStatistics, TimesStatistics
from ..prints.colors import Colors
from ..system.platform import Platform
from ..types.environments import Environments
from ..types.gitlab import MilestoneState

# Entrypoint class, pylint: disable=too-few-public-methods
class Entrypoint:

    # Enumerations
    Result = Enum('Result', [
        'SUCCESS',
        'FINALIZE',
        'ERROR',
        'CRITICAL',
    ])

    # CLI, pylint: disable=too-many-branches
    @staticmethod
    def cli(
        options: Namespace,
        environments: Environments,
    ) -> Result:

        # Variables
        project: Optional[GitLabProject] = None
        result: Entrypoint.Result

        # Header
        print(' ')

        # Parse URL variables
        gitlab_splits: urllib.parse.SplitResult = urllib.parse.urlsplit(options.url_path)
        gitlab_id: str = f'{gitlab_splits.netloc}'
        gitlab_url: str = f'{gitlab_splits.scheme}://{gitlab_splits.netloc}'
        gitlab_path: str = gitlab_splits.path.lstrip('/')

        # Prepare credentials
        private_token: str = environments.value('gitlab_token')
        job_token: str = environments.value('ci_job_token')
        ssl_verify: Union[bool, str] = True

        # Parse configuration files
        try:
            config: GitlabConfigParser
            if not private_token:
                config = GitlabConfigParser(gitlab_id, options.configs)
                private_token = str(config.private_token)
                if ssl_verify and (not config.ssl_verify
                                   or isinstance(config.ssl_verify, str)):
                    ssl_verify = config.ssl_verify
        except ConfigError as e:
            print(str(e))

        # GitLab client
        gitlab = GitLabFeature(
            url=gitlab_url,
            private_token=private_token,
            job_token=job_token,
            ssl_verify=ssl_verify,
        )
        print(f'{Colors.BOLD} - GitLab host: '
              f'{Colors.GREEN}{gitlab.url}'
              f'{Colors.RESET}')
        Platform.flush()

        # GitLab path
        project = gitlab.project(gitlab_path)
        print(f'{Colors.BOLD} - GitLab project: '
              f'{Colors.GREEN}{project.path_with_namespace}'
              f'{Colors.CYAN} ({project.description})'
              f'{Colors.RESET}')
        print(' ')
        Platform.flush()

        # Handle single project
        result = Entrypoint.project(
            options,
            gitlab,
            project.path_with_namespace,
        )
        if result != Entrypoint.Result.SUCCESS:
            return result

        # Result
        return Entrypoint.Result.SUCCESS

    # Project, pylint: disable=too-many-locals,too-many-statements
    @staticmethod
    def project(
        options: Namespace,
        gitlab: GitLabFeature,
        criteria: str,
    ) -> Result:

        # Variables
        milestone: MilestoneStatistics
        milestone_data: ProjectMilestone
        milestone_description: str
        milestones_statistics: Dict[str, MilestoneStatistics] = {}

        # Acquire project
        project = gitlab.project(criteria)

        # Show project details
        print(f'{Colors.BOLD} - GitLab project: '
              f'{Colors.YELLOW_LIGHT}{project.path_with_namespace} '
              f'{Colors.CYAN}({project.description})'
              f'{Colors.RESET}')
        Platform.flush()

        # Create milestone
        if options.create_milestone:

            # Validate issues feature
            if not project.issues_enabled:
                raise RuntimeError('GitLab issues feature not enabled')

            # Create new milestone
            project.milestones.create({
                'title': options.milestone,
            })

        # Get milestone
        elif options.get_milestone:

            # Validate issues feature
            if not project.issues_enabled:
                raise RuntimeError('GitLab issues feature not enabled')

            # Find milestone
            try:
                milestone_data = next(
                    milestone_data
                    for milestone_data in project.milestones.list(get_all=True)
                    if milestone_data.title == options.milestone
                    and isinstance(milestone_data, ProjectMilestone))
            except StopIteration as exc:
                raise GitlabGetError(
                    f'Could not find milestone \'{options.milestone}\' in project \'{criteria}\''
                ) from exc

            # Show milestone
            print(' ')
            print(f'{Colors.BOLD}   - Milestone: '
                  f'{Colors.CYAN}{milestone_data.title}'
                  f'{Colors.RESET}')
            print(f'{Colors.BOLD}     - Description: '
                  f'{Colors.GREEN}{milestone_data.description or "/"}'
                  f'{Colors.RESET}')
            print(f'{Colors.BOLD}     - State: '
                  f'{Colors.GREEN}{milestone_data.state or "?"}'
                  f'{Colors.RESET}')
            print(f'{Colors.BOLD}     - Start date: '
                  f'{Colors.GREEN}{milestone_data.start_date or "/"}'
                  f'{Colors.RESET}')
            print(f'{Colors.BOLD}     - Due date: '
                  f'{Colors.GREEN}{milestone_data.due_date or "/"}'
                  f'{Colors.RESET}')
            Platform.flush()

        # Set milestone settings
        if options.set_milestone_description \
                or options.set_milestone_state \
                or options.set_milestone_start_date \
                or options.set_milestone_due_date:

            # Find milestone
            try:
                milestone_data = next(
                    milestone_data
                    for milestone_data in project.milestones.list(get_all=True)
                    if milestone_data.title == options.milestone
                    and isinstance(milestone_data, ProjectMilestone))
            except StopIteration as exc:
                raise GitlabGetError(
                    f'Could not find milestone \'{options.milestone}\' in project \'{criteria}\''
                ) from exc

            # Show milestone
            print(' ')
            print(f'{Colors.BOLD}   - Milestone: '
                  f'{Colors.CYAN}{milestone_data.title or "/"}'
                  f'{Colors.RESET}')

            # Set milestone description
            if options.set_milestone_description is not None:
                milestone_data.description = options.set_milestone_description
                print(f'{Colors.BOLD}     - Set milestone description: '
                      f'{Colors.CYAN}{milestone_data.description or "/"}'
                      f'{Colors.RESET}')
                Platform.flush()

            # Set milestone state
            if options.set_milestone_state:
                if options.set_milestone_state not in MilestoneState.names():
                    raise SyntaxError(f'Unknown state: {options.set_milestone_state}'
                                      f' ({",".join(MilestoneState.names())})')
                milestone_data.state_event = options.set_milestone_state
                print(f'{Colors.BOLD}     - Set milestone state: '
                      f'{Colors.CYAN}{milestone_data.state_event}'
                      f'{Colors.RESET}')
                Platform.flush()

            # Set milestone start date
            if options.set_milestone_start_date is not None:
                milestone_data.start_date = options.set_milestone_start_date
                print(f'{Colors.BOLD}     - Set milestone start date: '
                      f'{Colors.CYAN}{milestone_data.start_date or "/"}'
                      f'{Colors.RESET}')
                Platform.flush()

            # Set milestone due date
            if options.set_milestone_due_date is not None:
                milestone_data.due_date = options.set_milestone_due_date
                print(f'{Colors.BOLD}     - Set milestone due date: '
                      f'{Colors.CYAN}{milestone_data.due_date or "/"}'
                      f'{Colors.RESET}')
                Platform.flush()

            # Save milestone
            milestone_data.save()

        # Detect milestones
        if options.milestones_statistics:

            # Validate issues feature
            if not project.issues_enabled:
                raise RuntimeError('GitLab issues feature not enabled')

            # Issues without milestone
            if not options.milestone or options.milestone == 'None':
                milestones_statistics[''] = MilestoneStatistics('Without milestone', )
                milestones_statistics[''].assignees[''] = AssigneeStatistics(
                    'Without assignee', )

            # Iterate through milestones
            for milestone_obj in sorted(
                    project.milestones.list(
                        get_all=True,
                        state='active' if options.exclude_closed_milestones else None,
                    ), key=lambda milestone: milestone.due_date
                    if milestone.due_date else MilestoneDescription.DUE_DATE_UNDEFINED,
                    reverse=False):

                # Filter specific milestone
                if options.milestone and options.milestone != 'None' and options.milestone not in [
                        str(milestone_obj.id), milestone_obj.title
                ]:
                    continue

                # Issues with milestone
                milestones_statistics[milestone_obj.id] = MilestoneStatistics(
                    milestone_obj.title, )
                milestones_statistics[
                    milestone_obj.id].assignees[''] = AssigneeStatistics(
                        'Without assignee', )

            # Iterate through issues
            for issue in project.issues.list(
                    get_all=True,
                    order_by='created_at',
                    sort='asc',
                    state='opened' if options.exclude_closed_issues else None,
            ):

                # Validate milestone ID
                milestone_id = issue.milestone[
                    'id'] if issue.milestone and 'id' in issue.milestone else ''
                if not milestone_id:
                    if not options.ignore_issues_without_milestone:
                        print(f'{Colors.BOLD}   - GitLab issue: '
                              f'{Colors.RED}Issue #{issue.iid}'
                              f'{Colors.GREY} ({issue.title})'
                              f'{Colors.RED} is missing a known milestone...'
                              f'{Colors.RESET}')
                        print(f'{Colors.BOLD}     - URL: '
                              f'{Colors.CYAN}{issue.web_url}'
                              f'{Colors.RESET}')
                        return Entrypoint.Result.ERROR
                    continue
                if milestone_id not in milestones_statistics:
                    continue

                # Get milestone statistics
                milestone = milestones_statistics[milestone_id]

                # Parse issue timings
                defaulted: bool = 'time_estimate' not in issue.time_stats(
                ) or issue.time_stats()['time_estimate'] == 0
                if not defaulted:
                    if issue.state != 'closed':
                        time_estimate = issue.time_stats()['time_estimate']
                        time_spent = issue.time_stats()['total_time_spent']
                    else:
                        time_estimate = issue.time_stats()['time_estimate']
                        time_spent = time_estimate
                else:
                    time_estimate = int(options.default_estimate) * 60 * 60
                    if issue.state != 'closed':
                        time_spent = 0
                    else:
                        time_spent = time_estimate

                # Handle milestone statistics
                milestone.issues_count += 1
                if not milestone.times.defaulted and defaulted:
                    milestone.times.defaulted = True
                milestone.times.estimates += time_estimate
                milestone.times.spent += time_spent

                # Prepare issue assignee
                assignee_id = issue.assignee[
                    'id'] if issue.assignee and 'id' in issue.assignee else ''
                if assignee_id not in milestone.assignees:
                    milestone.assignees[assignee_id] = AssigneeStatistics(
                        issue.assignee['name'], )

                # Handle assignee statistics
                milestone.assignees[assignee_id].issues_count += 1
                if not milestone.assignees[assignee_id].times.defaulted and defaulted:
                    milestone.assignees[assignee_id].times.defaulted = True
                milestone.assignees[assignee_id].times.estimates += time_estimate
                milestone.assignees[assignee_id].times.spent += time_spent

                # Dump issue object
                if options.dump:
                    print(' ')
                    print(issue.to_json())

            # Create milestones statistics
            for milestone_id, milestone in milestones_statistics.items():
                if not milestone.issues_count:
                    continue

                # Create milestone section
                outputs: List[str] = []
                outputs += ['']
                outputs += [f'# Milestone statistics - {milestone.title}']
                outputs += ['']

                # Create milestone table
                outputs += [
                    '| Assignees | Issues | Estimated | Spent | Remaining | Progress |'
                ]
                outputs += [
                    '|-----------|--------|-----------|-------|-----------|----------|'
                ]

                # Inject milestone table per assignee
                for _, assignee in milestone.assignees.items():
                    if not assignee.issues_count:
                        continue
                    times = assignee.times
                    outputs += [
                        f'| **{assignee.name}** '
                        f'| {assignee.issues_count} '
                        f'| {TimesStatistics.human(times.estimates, times.defaulted)} '
                        f'| {TimesStatistics.human(times.spent, times.defaulted)} '
                        f'| {TimesStatistics.human(times.remaining, times.defaulted)} '
                        f'| {times.progress()} '
                        f'|'
                    ]

                # Inject milestone table total
                times = milestone.times
                outputs += [
                    '| _**Total**_ '
                    f'| _{milestone.issues_count}_ '
                    f'| _{TimesStatistics.human(times.estimates, times.defaulted)}_ '
                    f'| _{TimesStatistics.human(times.spent, times.defaulted)}_ '
                    f'| {TimesStatistics.human(times.remaining, times.defaulted)} '
                    f'| _{times.progress()}_ '
                    '|'
                ]

                # Export to terminal
                for line in outputs:
                    print(f' {line}')

                # Export to milestone
                if milestone_id:
                    milestone_obj = project.milestones.get(milestone_id)
                    milestone_description = MilestoneDescription.inject_statistics(
                        description=milestone_obj.description,
                        statistics='\n'.join(outputs),
                    )
                    if MilestoneDescription.updated_statistics(milestone_obj.description,
                                                               milestone_description):
                        milestone_obj.description = milestone_description
                        milestone_obj.save()

        # Dump project object
        if options.dump:
            print(' ')
            print(project.to_json())

        # Footer
        print(' ')
        Platform.flush()

        # Result
        return Entrypoint.Result.SUCCESS
